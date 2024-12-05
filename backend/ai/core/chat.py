import itertools
import os
import re
from typing import Iterator, List
from urllib.parse import unquote

from diskcache import FanoutCache

from ai.core.custom_litellm import completion
from ai.core.models import ChatMessage, ChatRequestBody
from ai.core.prompts import SYSTEM_PROMPT
from app.core.dbt import LiveDBTParser
from app.models import Asset, AssetLink, Column, ColumnLink
from app.models.project import Project
from app.models.resources import DBTCoreDetails
from app.models.user import User
from app.models.workspace import Workspace
from app.services.lineage_service import Lineage

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


def recreate_lineage_object(
    asset_id: str | None,
    related_assets: List[dict] | None,
    asset_links: List[dict] | None,
    column_links: List[dict] | None,
) -> Lineage | None:
    if (
        asset_id is None
        or related_assets is None
        or asset_links is None
        or column_links is None
    ):
        return None
    assets, columns = zip(*[get_asset_object(d) for d in related_assets])
    columns = list(itertools.chain(*columns))
    asset_links = [AssetLink(**link) for link in asset_links]
    column_links = [ColumnLink(**link) for link in column_links]
    return Lineage(
        asset_id=asset_id,
        assets=assets,
        columns=columns,
        asset_links=asset_links,
        column_links=column_links,
    )


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


def asset_md(asset: Asset, columns: dict, contents: str):
    description = asset.description or ""
    columns_md = [
    ]
    for key, col in columns.items():
        columns_md.append(
            f"-{col.get('name')}:{col.get('type')} {col.get('comment') or ''}"
        )
    return f"""
model:{asset.name}
description:{description}

columns:
{'\n'.join(columns_md)}

contents:
```sql
{contents}
```
"""


def build_context(
    lineage: Lineage | None,
    message_history: List[ChatMessage],
    dbt_details: DBTCoreDetails,
    project_id: str,
    context_files: List[str] | None = None,
):
    user_instruction = next(
        msg.content for msg in reversed(message_history) if msg.role == "user"
    )
    resource = dbt_details.resource
    project = Project.objects.get(id=project_id)

    with dbt_details.dbt_transition_context() as (transition, project_path, _):
        with project.repo_context() as (repo, _):
            transition.mount_manifest(defer=True)
            asset_mds = []
            if lineage:
                for asset in lineage.assets:
                    # find each file for the related assets
                    manifest_node = LiveDBTParser.get_manifest_node(
                        transition.after, asset.unique_name
                    )
                    if not manifest_node:
                        continue
                    catalog_node = LiveDBTParser.get_catalog_node(
                        transition.after, asset.unique_name
                    )
                    if catalog_node:    
                        columns = catalog_node.get("columns", {})
                    else:
                        columns = {}
                    path = os.path.join(
                        project_path, manifest_node.get("original_file_path")
                    )
                    if not os.path.exists(path):
                        continue
                    with open(path) as file:
                        contents = file.read()
                        asset_mds.append(
                            asset_md(
                                asset,
                                columns,
                                contents,
                            )
                        )
            file_contents = [
                open(os.path.join(repo.working_tree_dir, unquote(path)), "r").read()
                for path in context_files
            ]

            edges = []
            if lineage:
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

            # File contents
            output = f"""{dialect_md}
{lineage_md}
{assets}
    """
            if file_contents:
                file_content_blocks = []
                for content in file_contents:
                    file_content_blocks.append(f"```sql\n{content}\n```")

                output += f"""
    Context Files:
    {"\n".join(file_content_blocks)}
    """
            output += f"\nUser Instructions: {user_instruction}\n\nAnswer the user's question based on the above context. Do not answer anything else, just answer the question."
            return output


def stream_chat_completion(
    *,
    payload: ChatRequestBody,
    dbt_details: DBTCoreDetails,
    workspace: Workspace,
    user: User,
) -> Iterator[str]:
    if payload.model.startswith("claude"):
        api_key = workspace.anthropic_api_key
    elif payload.model.startswith("gpt") or payload.model.startswith("o1"):
        api_key = workspace.openai_api_key
    else:
        raise ValueError(f"Unsupported model: {payload.model}")
    if api_key is None:
        raise ValueError("NO_API_KEY")

    lineage = recreate_lineage_object(
        asset_id=payload.asset_id,
        related_assets=payload.related_assets,
        asset_links=payload.asset_links,
        column_links=payload.column_links,
    )
    prompt = build_context(
        lineage=lineage,
        message_history=payload.message_history,
        dbt_details=dbt_details,
        context_files=payload.context_files,
        project_id=payload.project_id,
    )
    message_history = []
    for idx, msg in enumerate(payload.message_history):
        if idx == len(payload.message_history) - 1 and prompt:
            msg.content = prompt
        message_history.append(msg.model_dump())

    messages = [
        {"content": SYSTEM_PROMPT, "role": "system"},
        *message_history,
    ]

    response = completion(
        api_key=api_key,
        temperature=0.3,
        model=payload.model,
        messages=messages,
        stream=True,
        user_id=user.id,
    )

    for chunk in response:
        yield chunk.choices[0].delta.content or ""
