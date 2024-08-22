from typing import Any

import instructor
import numpy  # noqa
import orjson
from litellm import completion
from mpire import WorkerPool
from pydantic import BaseModel, create_model
from tqdm import tqdm
from typing import TypedDict

from ai.embeddings import DEFAULT_EMBEDDING_MODEL, EmbeddingModes, embed
from vinyl.lib.dbt import DBTProject


class ModelDescription(BaseModel):
    description: str


class ColumnDescription(BaseModel):
    description: str


MODEL_SYSTEM_PROMPT = """
Instructions:
- You are an expert AI data analyst.
- Given a dbt model's name, schema, and underlying sql, write a description for that model.

Rules:
- Respond in a few paragraphs.
- Use clear language.
- Explain the purpose of the model and how it can be used in real-world applications. 
- Highlight the significant patterns and correlations that can be discovered in the data, as well as any key features.  
- Avoid first-person language like "we" and "us". 
- Where applicable, usse analogies or examples to clarify any technical terms or concepts.
"""

COLUMN_SYSTEM_PROMPT = """
Instructions:
- You are an expert AI data analyst.
- Given a dbt model's name, schema, underlying sql, and columns to describe, write a clear and concise description for each column.

Rules:
- Describe the purpose and meaning of each column, including any unique details or logic that would be useful for review. 
- Ensure that your descriptions are informative and help stakeholders understand the model's data in an straightforward manner.  
- Use plain language that is accessible to all stakeholders
- Avoid complex technical jargon
- Don't start your description with filler works like "This column is used to..." or "This column represents...". Just describe the column directly.
- Use analogies or examples where necessary to clarify technical terms or concepts.
"""

def get_schema_description(columnName: str, columnType: str):
    return f"- {columnName}: {columnType}"

def get_schema_and_compiled_sql(
    dbtproj: DBTProject, dbt_node_name: str, compile_if_not_found=True
):
    # prepare dbtproj
    dbtproj.mount_manifest()
    dbtproj.mount_catalog()
    columns = dbtproj.catalog["nodes"].get(dbt_node_name, {}).get("columns", {})

    compiled_sql = dbtproj.get_compiled_sql(
        dbt_node_name, compile_if_not_found=compile_if_not_found
    )[0]

    return "\n".join(
        [get_schema_description(columnName=k, columnType=v) for k, v in columns.items()]
    ), compiled_sql


def get_chat_completion(
    system_instructions_content: str,
    prompt_content: str,
    response_model: ModelDescription | ColumnDescription,
    ai_model_name="gpt-4o",
):
    client = instructor.from_litellm(completion, temperature=0)
    resp = client.chat.completions.create(
        model=ai_model_name,
        messages=[
            {
                "role": "system",
                "content": system_instructions_content,
            },
            {"role": "user", "content": prompt_content},
        ],
        response_model=response_model,
    )

    return resp.description


def get_table_completion(
    model_name: str,
    schema: str,
    compiled_sql: str,
    ai_model_name="gpt-4o",
):
    content = f"model name: {model_name.split('.')[-1]}\n\n"
    content += f"schema:\n{schema}\n\n"
    content += f"compiled_sql:\n{compiled_sql}"

    return get_chat_completion(
        system_instructions_content=MODEL_SYSTEM_PROMPT,
        prompt_content=content,
        ai_model_name=ai_model_name,
        response_model=ModelDescription,
    )


def get_table_completion_from_dbt(
    dbtproj: DBTProject,
    dbt_node_name: str,
    ai_model_name="gpt-4o",
    compile_if_not_found=True,
):
    schema, compiled_sql = get_schema_and_compiled_sql(
        dbtproj, dbt_node_name, compile_if_not_found=compile_if_not_found
    )

    return get_table_completion(
        model_name=dbt_node_name.split(".")[-1],
        schema=schema,
        compiled_sql=compiled_sql,
        ai_model_name=ai_model_name,
    )


def get_column_completion_from_dbt(
    dbtproj: DBTProject,
    dbt_model_column_names: dict[str, Any],
    include_nested_fields: bool = False,
    ai_model_name="gpt-4o",
    max_columns_per_batch=15,
    compile_if_not_found=True,
    progress_bar=True,
    parallel=True,
):
    dbt_model_data = {}
    for model_name in dbt_model_column_names:
        schema, compiled_sql = get_schema_and_compiled_sql(
            dbtproj, model_name, compile_if_not_found=compile_if_not_found
        )
        dbt_model_data[model_name] = {
            "schema": schema,
            "compiled_sql": compiled_sql,
            "column_names": dbt_model_column_names[model_name],
        }

    return get_column_completion(
        dbt_model_data=dbt_model_data,
        include_nested_fields=include_nested_fields,
        ai_model_name=ai_model_name,
        max_columns_per_batch=max_columns_per_batch,
        progress_bar=progress_bar,
        parallel=parallel,
    )


class ModelData(TypedDict):
    schema: str
    compiled_sql: str
    column_names: list[str]


def get_column_completion(
    dbt_model_data: dict[str, ModelData],
    include_nested_fields: bool = False,
    ai_model_name="gpt-4o",
    max_columns_per_batch=15,
    progress_bar=True,
    parallel=True,
):
    def helper(model_name: str, colnames_orjson: str):
        colnames = orjson.loads(colnames_orjson)
        fields = {f"{k}": (ColumnDescription, ...) for k in colnames}
        ColumnDescriptionModel = create_model("ColumnDescriptionModel", **fields)
        content = f"model name: {model_name.split('.')[-1]}\n\n"
        content += f"schema:\n{schema}\n\n"
        content += f"compiled_sql:\n{compiled_sql}\n\n"
        content += "column_names_to_describe:"
        for colname in colnames:
            content += f"\n- {colname}"
        try:
            resp = get_chat_completion(
                system_instructions_content=COLUMN_SYSTEM_PROMPT,
                prompt_content=content,
                ai_model_name=ai_model_name,
                response_model=ColumnDescriptionModel,
            )

            return {
                model_name: {k: v["description"] for k, v in resp.model_dump().items()}
            }
        except Exception as e:  # noqa
            print(e)
            pass

    schema_dict = {}
    compiled_sql_dict = {}
    batches = []
    for model_name in dbt_model_data:
        model_data = dbt_model_data[model_name]
        schema = model_data["schema"]
        compiled_sql = model_data["compiled_sql"]
        column_names = model_data["columns"]

        schema_dict[model_name] = schema
        compiled_sql_dict[model_name] = compiled_sql

        if column_names is None:
            column_names = [k["col_name"] for k in schema]

        if not include_nested_fields:
            column_names = [k for k in column_names if "." not in k]

        if (
            max_columns_per_batch is not None
            and len(column_names) > max_columns_per_batch
        ):
            batches_it = [
                (model_name, orjson.dumps(column_names[i : i + max_columns_per_batch]))
                for i in range(0, len(column_names), max_columns_per_batch)
            ]
        else:
            batches_it = [(model_name, orjson.dumps(column_names))]
        batches.extend(batches_it)

    if parallel and len(batches) > 1:
        with WorkerPool() as pool:
            results = pool.map(helper, batches, progress_bar=progress_bar)

    else:
        results = []
        adj_batches = tqdm(batches) if progress_bar else batches
        for batch in adj_batches:
            results.append(helper(*batch))

    out = {}
    for res in results:
        for k, v in res.items():
            for k2, v2 in v.items():
                out.setdefault(k, {})[k2] = v2

    return out


def get_embeddings(
    dbtproj: DBTProject,
    dbt_asset_info: dict[str, Any],
    ai_model_name=DEFAULT_EMBEDDING_MODEL,
    mode: EmbeddingModes = EmbeddingModes.AUTOCOMPLETE,
) -> list[list[float]]:
    to_embed = []
    for asset in dbt_asset_info:
        model_ai_description = asset["ai_description"]
        column_ai_descriptions = "\n".join(
            [f"- {v['name']}: {v['ai_description']}" for v in asset["columns"]]
        )
        base_content = f"{asset['type']} name: {asset['name']}\n{asset['type']} description: {model_ai_description}"
        if mode == "autocomplete":
            content = (
                f"{base_content}\n\ncolumn descriptions:\n{column_ai_descriptions}"
            )
        else:
            content = base_content
            if tags := asset.get("tags"):
                content += f"\n\ntags: {tags}"
            if materialization := asset.get("materialization"):
                content += f"\n\nmaterialization: {materialization}"
            if db_location := asset.get("db_location"):
                content += f"\n\ndb_location: {db_location}"
        to_embed.append(content)
    return embed(ai_model_name, to_embed)
