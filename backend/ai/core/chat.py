import itertools
import os
import re
from typing import Iterator, List
from urllib.parse import unquote

import sentry_sdk

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
    columns_md = []
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


def get_assets_from_lineage(dbt_details: DBTCoreDetails | None = None, lineage: Lineage | None = None) -> List[str]:
    if lineage is None or dbt_details is None:
        return []

    with dbt_details.dbt_transition_context() as (transition, project_path, _):
        transition.mount_manifest(defer=True)
        assets = []
        if lineage:
            for asset in lineage.assets:
                manifest_node = LiveDBTParser.get_manifest_node(
                    transition.after, asset.unique_name
                )
                if not manifest_node:
                    continue
                catalog_node = LiveDBTParser.get_catalog_node(
                    transition.after, asset.unique_name
                )
                columns = catalog_node.get("columns", {}) if catalog_node else {}
                path = os.path.join(
                    project_path, manifest_node.get("original_file_path")
                )
                if not os.path.exists(path):
                    continue
                with open(path) as file:
                    contents = file.read()
                    assets.append(asset_md(asset, columns, contents))
    return assets


def build_context(
    lineage: Lineage | None,
    message_history: List[ChatMessage],
    dialect: str,
    dbt_details: DBTCoreDetails | None = None,
    context_files: List[str] | None = None,
    context_preview: str | None = None,
    compiled_query: str | None = None,
    file_problems: List[str] | None = None,
    custom_selections: List[str] | None = None,
):
    user_instruction = next(
        msg.content for msg in reversed(message_history) if msg.role == "user"
    )

    asset_mds = get_assets_from_lineage(dbt_details, lineage)
    assets_str = "\n".join(asset_mds)

    file_content_blocks = [
        f"```sql\n{content}\n```"
        for content in context_files
    ]

    file_contents_str = (
        "\n".join(file_content_blocks) if file_content_blocks else ""
    )

    edges = []
    if lineage:
        for link in lineage.asset_links:
            source_model = extract_model_name(link.source_id)
            target_model = extract_model_name(link.target_id)
            edges.append({"source": source_model, "target": target_model})

    file_problems_str = "\n".join(file_problems) if file_problems else None
    custom_selections_str = "\n".join(
        f"Selected code from {selection.file_name} (lines {selection.start_line}-{selection.end_line}):\n```{selection.selection}```\n"
        for selection in custom_selections
    ) if custom_selections else None
    lineage_str = f"Model lineage\nIMPORTANT: keep in mind how these are connected to each other. You may need to add or modify this structure to complete a task.\n{lineage_ascii(edges)}" if edges else None

    output = f"""
# Dialect
Use the {dialect} dialect when writing any sql code.

{lineage_str}

{assets_str}

{f"Context Files:\n{file_contents_str}" if file_contents_str else ''}

{f"Custom Selections. These are selections of files that the user has selected to include in the context. Pay close attention to these files.\n{custom_selections_str}" if custom_selections_str else ''}

{f"Preview of active file:\n\n{context_preview}" if context_preview else ''}

{f"Compiled Query:\n\n```sql\n{compiled_query}\n```" if compiled_query else ''}

{f"File Problems:\n{file_problems_str}" if file_problems_str else ''}
User Instructions: {user_instruction}

Answer the user's question based on the above context. Do not answer anything else, just answer the question.
"""

    return output


def stream_chat_completion(
    *,
    payload: ChatRequestBody,
    dialect: str,
    api_keys: dict,
    dbt_details: DBTCoreDetails | None = None,
    user_id: str | None = None,
    workspace_instructions: str | None = None,
    tags: List[str] | None = None,
) -> Iterator[str]:
    if payload.model.startswith("claude"):
        api_key = api_keys["anthropic"]
    elif payload.model.startswith("gpt") or payload.model.startswith("o1"):
        api_key = api_keys["openai"]
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
        context_preview=payload.context_preview,
        compiled_query=payload.compiled_query,
        file_problems=payload.file_problems,
        custom_selections=payload.custom_selections,
        dialect=dialect,
    )
    message_history = []
    for idx, msg in enumerate(payload.message_history):
        if idx == len(payload.message_history) - 1 and prompt:
            msg.content = prompt
        if not msg.content or msg.content.strip() == "":
            sentry_sdk.capture_message(
                f"Empty message content: {payload.message_history}",
                level="warning",
            )
            continue
        message_history.append(msg.model_dump())

    system_prompt = f"""{SYSTEM_PROMPT}

Here are some additional instructions set by the user for you to follow. These are very important and you must follow them.
{workspace_instructions}
"""
    messages = [
        {"content": system_prompt, "role": "system"},
        *message_history,
    ]

    response = completion(
        api_key=api_key,
        temperature=0.3,
        model=payload.model,
        messages=messages,
        stream=True,
        user_id=user_id,
        tags=["chat", *(tags or [])],
    )

    for chunk in response:
        yield chunk.choices[0].delta.content or ""
