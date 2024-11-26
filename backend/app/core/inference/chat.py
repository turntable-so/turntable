import itertools
import os
import re
from typing import List

import pandas as pd
from diskcache import FanoutCache
from ibis.expr.types import Table
from litellm import completion
from mpire import WorkerPool
from pydantic import BaseModel

from app.core.dbt import LiveDBTParser
from app.core.inference.prompts import CHAT_PROMPT_NO_CONTEXT
from app.models import Asset, AssetLink, Column, ColumnLink, Resource, User
from app.services.lineage_service import Lineage
from app.utils.df import get_first_n_values, truncate_values
from vinyl.lib.table import VinylTable

cache = FanoutCache(directory="/cache", shards=10, timeout=300)


def get_asset_object(asset_dict: dict):
    unused_asset_keys = [
        "resource_type",
        "resource_subtype",
        "resource_has_dbt",
        "resource_name",
        "url",
    ]
    unused_column_keys = ["is_unused"]
    for key in unused_asset_keys:
        if key in asset_dict:
            asset_dict.pop(key)
    if "columns" in asset_dict:
        columns = asset_dict.pop("columns")
        for col in columns:
            for key in unused_column_keys:
                if key in col:
                    col.pop(key)
    asset_dict["db_location"] = [
        asset_dict.pop("dataset"),
        asset_dict.pop("schema"),
        asset_dict.pop("table_name"),
    ]
    asset = Asset(**asset_dict)
    return asset, [Column(**col, asset_id=asset.id) for col in columns]


def recreate_lineage_object(data: dict) -> Lineage:
    assets, columns = zip(*[get_asset_object(d) for d in data.get("related_assets")])
    columns = list(itertools.chain(*columns))
    asset_links = [AssetLink(**link) for link in data.get("asset_links")]
    column_links = [ColumnLink(**link) for link in data.get("column_links")]
    print(data.get("asset_id"))
    return Lineage(
        asset_id=data.get("asset_id"),
        assets=assets,
        columns=columns,
        asset_links=asset_links,
        column_links=column_links,
    )


@cache.memoize(tag="query2")
def run_query(query: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    connector = resource.details.get_connector()
    return connector.run_query(query)[0]


@cache.memoize(tag="eda2")
def get_eda_sql(table: Table, column: str, dialect: str, topk: int = 5):
    vinyltable = VinylTable(table._arg)
    return vinyltable.eda(cols=[column], topk=topk, topk_col_name=False).to_sql(
        dialect=dialect, node_name=""
    )


def get_asset_eda(asset: Asset, resource: Resource, topk: int = 5):
    db, schema, table = asset.db_location
    connector = resource.details.get_connector()
    table = connector._get_table(database=db, schema=schema, table=table)
    print("table", table)
    print("table.columns", table.columns)
    dialect = resource.details.subtype
    sqls = [get_eda_sql(table, col, dialect, topk) for col in table.columns]

    with WorkerPool(n_jobs=10, start_method="threading", use_dill=True) as pool:
        dfs = pool.imap_unordered(run_query, [(sql, resource.id) for sql in sqls])
    df = pd.concat(dfs)

    df["distinct_frac"] = df["distinct_frac"].round(3)

    # Truncate max/min values that are too long
    df["max"] = df["max"].apply(truncate_values())
    df["min"] = df["min"].apply(truncate_values())

    # For low cardinality columns, only show first value
    def transform_row(row):
        values, n_added = get_first_n_values()(row["top_values"])
        return pd.Series(
            {
                "top_values": values,
                "top_value_counts": row["top_value_counts"][:n_added],
            }
        )

    # filter = (df["n_distinct"] > 1000) & (df["distinct_frac"] < 0.001)
    filter = df["type"] == "json"
    df.loc[filter, ["top_values", "top_value_counts"]] = df[filter].apply(
        transform_row,
        axis=1,
    )
    # for non-json columns, truncate the values
    filter = df["type"] != "json"
    for col in ["min", "max"]:
        df.loc[filter, col] = df.loc[filter, col].apply(truncate_values())
    df.loc[filter, "top_values"] = df.loc[filter, "top_values"].apply(
        lambda x: [truncate_values()(v) for v in x]
    )
    df.reset_index(drop=True)
    df.sort_values(by="position", inplace=True)
    return df


def asset_md(asset: Asset, resource: Resource, contents: str):
    column_table = get_asset_eda(asset, resource, 30).to_csv(index=False)
    description = asset.description or ""
    return f"""
## {asset.name}
{description}

## Schema and profiling info
{column_table}

## Contents
```sql
{contents}
```
"""


def extract_model_name(urn_string):
    pattern = r",[^,]+\.([^,]+),[^)]+\)$"
    match = re.search(pattern, urn_string)
    if match:
        return match.group(1)
    return None


def lineage_ascii(edges):
    # Build the graph
    graph = {}
    all_nodes = set()
    for edge in edges:
        source, target = edge["source"], edge["target"]
        if source not in graph:
            graph[source] = set()
        graph[source].add(target)
        all_nodes.add(source)
        all_nodes.add(target)

    # Find root nodes (nodes with no incoming edges)
    root_nodes = all_nodes - set().union(*graph.values())

    def print_node(node, prefix="", is_last=True):
        result = prefix
        result += "└── " if is_last else "├── "
        result += f"{node}\n"

        if node in graph:
            children = sorted(graph[node])
            for i, child in enumerate(children):
                next_prefix = prefix + ("    " if is_last else "│   ")
                result += print_node(child, next_prefix, i == len(children) - 1)

        return result

    ascii_graph = "```\n"
    for i, root in enumerate(sorted(root_nodes)):
        ascii_graph += print_node(root, "", i == len(root_nodes) - 1)
    ascii_graph += "```"

    return ascii_graph


def build_context(
    user: User,
    lineage: Lineage,
    instructions: str,
    current_file: str = None,
):
    # map each id to a schema (with name, type and description)
    if not lineage.assets or len(lineage.assets) == 0:
        return f"\nUser Instructions: {instructions}\n"
    workspace = user.current_workspace()
    dbt_details = workspace.get_dbt_dev_details()
    resource = dbt_details.resource

    with dbt_details.dbt_transition_context() as (
        transition,
        project_path,
        repo,
    ):
        transition.mount_manifest(defer=True)
        asset_mds = []

        # schemas
        for asset in lineage.assets:
            # don't include the current asset
            if asset.id == lineage.asset_id:
                continue

            # find each file for the related assets
            manifest_node = LiveDBTParser.get_manifest_node(
                transition.after, asset.unique_name
            )
            if not manifest_node:
                continue
            path = os.path.join(project_path, manifest_node.get("original_file_path"))
            if not os.path.exists(path):
                continue
            with open(path) as file:
                contents = file.read()
                asset_mds.append(
                    asset_md(
                        asset,
                        resource,
                        contents,
                    )
                )

        # lineage information
        edges = []
        for link in lineage.asset_links:
            source_model = extract_model_name(link.source_id)
            target_model = extract_model_name(link.target_id)
            edges.append({"source": source_model, "target": target_model})

        dialect_md = f"""
# Dialect
Use the {resource.details.subtype} dialect when writing any sql code.
"""

        lineage_md = f"""
# Model lineage
IMPORTANT: keep in mind how these are connected to each other. You may need to add or modify this structure to complete a task.
{lineage_ascii(edges)}
"""
        assets = "\n".join(asset_mds)
        # file contents
        output = f"""{dialect_md}
{lineage_md}
{assets}
User Instructions: {instructions}
"""
        if current_file:
            output += f"""
Current File:
```sql
{current_file}
```
"""
        print("output", output)
        return output


class RelatedAsset(BaseModel):
    id: str
    unique_name: str
    name: str
    path: str


class Context(BaseModel):
    current_file: str
    related_asset: List[RelatedAsset]


def chat_completion(user_prompt: str):
    return completion(
        temperature=0,
        model="gpt-4o",
        messages=[
            {"content": CHAT_PROMPT_NO_CONTEXT, "role": "system"},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
