CHAT_PROMPT_NO_CONTEXT = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.

Rules:
- Be as helpful as possible and answer all questions to the best of your ability.
- Please reference the latest dbt documentation at docs.getdbt.com if needed
- You will only respond in markdown, using headers, paragraph, bulleted lists and sql/dbt code blocks if needed for the best answer quality possible
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
"""
from typing import List
from litellm import completion
from pydantic import BaseModel


import os

from django.core.management.base import BaseCommand
from app.models import Asset
import re

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

"""

EDIT_PROMPT_SYSTEM = """
You are an expert data analyst and data engineer who is a world expert at dbt (data build tool.
You have mastery in writing sql, jinja, dbt macros and architecturing data pipelines using marts, star schema architecures and designs for efficient and effective analytics data pipelines.

You are given a dbt model file and a user request to edit the file.

Rules:
- You will only respond with the modified file contents. No markdown or natural language will be accepted except as comments
- IMPORTANT: make sure all generate sql, dbt jinja examples or included code blocks are syntactically correct and will run on the target database postgres
- IMPORTANT: only respond with the full modified file contents, no markdown allowed and no backticks
- You will be given context for tables upstream and downstream of a current_file. current_file is the file to edit and no other files.
- You are not allowed to tamper with the existing formatting
"""


def asset_md(asset: Asset, contents: str):
    columns = asset.columns.all()
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
    related_assets: List[str],
    instructions: str,
    asset_links: List[str],
    current_file: str = None,
):
    # map each id to a schema (with name, type and description)
    if related_assets and len(related_assets) > 0:
        assets = Asset.objects.filter(id__in=related_assets)

        dbt_details = assets[0].resource.dbtresource_set.first()
        with dbt_details.dbt_transition_context() as (
            transition,
            _,
            repo,
        ):
            transition.mount_manifest(defer=True)
            asset_mds = []
            # schemas
            for asset in assets:
                # find each file for the related assets
                with open(
                    os.path.join(
                        repo.working_tree_dir,
                        "models",
                        transition.after.manifest.get("nodes")
                        .get(asset.unique_name.lower())
                        .get("path"),
                    )
                ) as file:
                    contents = file.read()
                    asset_mds.append(asset_md(asset, contents))

            # lineage information
            edges = []
            for link in asset_links:
                source_model = extract_model_name(link["source_id"])
                target_model = extract_model_name(link["target_id"])
                edges.append({"source": source_model, "target": target_model})

            lineage_md = f"""
    # Model lineage
    IMPORTANT: keep in mind how these are connected to each other. You may need to add or modify this structure to complete a task.
    {lineage_ascii(edges)}
    """
            assets = "\n".join(asset_mds)
            # file contents
            output = f"""{lineage_md}
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
    else:

        return f"""
User Instructions: {instructions}
"""


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
