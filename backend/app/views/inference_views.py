# File: api/views/execute_query.py

import json
import os

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from app.models.workspace import Workspace
from litellm import completion

from rest_framework import status
from rest_framework.response import Response

from app.models.metadata import Asset
from litellm import completion

SYSTEM_PROMPT = """
You are an expert data analyst who is proficient at writing and modifying POSTGRES sql and dbt (data build tool) models.

Rules:
- You are tasked with modifying a dbt (data build tool) model includes editing sql, jinja templating or adding additional sql.
- You write syntactically correct sql that uses best practices such as using CTEs, qualifying columns and good variable name choices.
- You will ONLY respond with the changed code for the entire file. NEVER offer an explanation or other artifacts besides the entire dbt model file
- You will be provided with the schema for the dbt model as well as its data lineage and associated model schemas to help you write the sql transform that is correct and accurate
- Use {{ ref('<model_name>')}} when referencing tables in queries
- IMPORTANT: do not modify sql styling or formatting in any way
- Respond in markdown format and just reply with the sql in a code block
"""


def make_user_prompt(
    upstream_deps: str,
    schema: str,
    instructions: str,
    filename: str,
    file_contents: str,
):
    prompt = f"""
# Upstream dependencies
```
{upstream_deps}
```

# {filename} schema:

{schema}

Edit the dbt model given these instructions: {instructions}
```{filename}
{file_contents}
```
"""
    return prompt


def infer(user_prompt: str):
    return completion(
        temperature=0.0,
        model="gpt-4o",
        messages=[
            {"content": SYSTEM_PROMPT, "role": "system"},
            {"role": "user", "content": user_prompt},
        ],
    )


def edit_file(filepath: str, instruction: str, content: str):

    def extract_model_name(filepath):
        return filepath.split("/")[-1].split(".")[0]

    model_name = extract_model_name(filepath).upper()

    asset = Asset.objects.get(unique_name=f"MODEL.JAFFLE_SHOP.{model_name}")

    current_asset = {
        "description": asset.description,
        "name": asset.name,
        "columns": [
            {
                "name": column.name,
                "type": column.type,
                "description": column.description,
            }
            for column in asset.columns.all()
        ],
    }

    upstream_deps = [
        {
            "description": upstream_asset.description,
            "name": upstream_asset.name,
            "columns": [
                {
                    "name": column.name,
                    "type": column.type,
                    "description": column.description,
                }
                for column in upstream_asset.columns.all()
            ],
        }
        for upstream_asset in asset.get_upstream_assets()
    ]

    import yaml

    upstream_deps_yaml = yaml.dump(upstream_deps)
    schema_yml = yaml.dump(current_asset)

    user_prompt = make_user_prompt(
        upstream_deps=upstream_deps_yaml,
        schema=schema_yml,
        instructions=instruction,
        filename=filepath,
        file_contents=content,
    )

    response = infer(user_prompt)
    content = response.choices[0].message.content
    extracted_sql = content.split("```sql")[1].split("```")[0].strip()
    return extracted_sql


class InferenceView(APIView):
    def post(self, request):
        # Extract instructions from the request
        filepath = request.data.get("filepath")
        instructions = request.data.get("instructions")
        content = request.data.get("content")

        if not instructions:
            return Response(
                {"error": "No instructions provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not content:
            return Response(
                {"error": "No content provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not filepath:
            return Response(
                {"error": "No filepath provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Call the LLM for inference
        generated_content = edit_file(filepath, instructions, content)

        # Extract the generated content from the response
        return Response({"content": generated_content}, status=status.HTTP_200_OK)
