CHAT_PROMPT_NO_CONTEXT = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.

Rules:
- Be as helpful as possible and answer all questions to the best of your ability.
- Please reference the latest dbt documentation at docs.getdbt.com if needed
- You will only respond in markdown, using headers, paragraph, bulleted lists and sql/dbt code blocks if needed for the best answer quality possible
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
"""
import itertools
import os
import re
from typing import List

from litellm import completion
from pydantic import BaseModel

from app.core.dbt import LiveDBTParser
from app.models import Asset, AssetLink, Column, ColumnLink, User
from app.services.lineage_service import Lineage

SYSTEM_PROMPT = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.
You will be provided with dbt project context that includes:
1. The data lineage
2. table schemas 
3. file contents

Rules:
- Be as helpful as possible and answer all questions to the best of your ability.
- Please reference the latest dbt documentation at docs.getdbt.com if needed
- You may reference parts of the cntext that was passed in
- You will only respond in markdown, using headers, paragraph, bulleted lists and sql/dbt code blocks if needed for the best answer quality possible
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
- You will be provided the sql dialect. Make sure to use it when writing any sql code.
"""

EDIT_PROMPT_SYSTEM = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool).
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.

You are given a dbt model file and a user request to edit the file.

Rules:
- You will only respond with the modified file contents. No markdown or natural language will be accepted except as comments
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
- IMPORTANT: only respond with the full modified file contents, no markdown allowed and no backticks
- You will be given context for tables upstream and downstream of a current_file. current_file is the file to edit and no other files.
- You are not allowed to tamper with the existing formatting
- You will be provided the sql dialect. Make sure to use it when writing any sql code.
"""


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


def asset_md(lineage: Lineage, asset: Asset, contents: str):
    columns = [c for c in lineage.columns if c.asset_id == asset.id]
    column_table = (
        "| Name | Type | Description |\n|-------------|-----------|-------------|\n"
    )
    for column in columns:
        column_table += (
            f"| {column.name} | {column.type} | {column.description or ''} |\n"
        )

    description = asset.description or ""
    return f"""
## {asset.name}
{description}

## Schema
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
    dbt_details = workspace.get_dbt_details()
    with dbt_details.dbt_transition_context() as (
        transition,
        project_path,
        repo,
    ):
        transition.mount_manifest(defer=True)
        asset_mds = []
        # schemas
        for asset in lineage.assets:
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
                asset_mds.append(asset_md(lineage, asset, contents))

        # lineage information
        edges = []
        for link in lineage.asset_links:
            source_model = extract_model_name(link.source_id)
            target_model = extract_model_name(link.target_id)
            edges.append({"source": source_model, "target": target_model})

        dialect_md = f"""
# Dialect
Use the {dbt_details.resource.details.subtype} dialect when writing any sql code.
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
        temperature=0.5,
        model="gpt-4o",
        messages=[
            {"content": CHAT_PROMPT_NO_CONTEXT, "role": "system"},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
