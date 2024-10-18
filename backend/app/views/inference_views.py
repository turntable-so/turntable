# File: api/views/execute_query.py

import asyncio
import json
import os
import uuid

from django.views import View
from asgiref.sync import sync_to_async
from django.http import JsonResponse, StreamingHttpResponse
from app.models.workspace import Workspace
from litellm import completion
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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


sessions = {}


@method_decorator(csrf_exempt, name="dispatch")
class InferenceView(View):
    content_negotiation_class = None  # Disable content negotiation

    async def post(self, request):
        # Extract instructions from the request
        data = json.loads(request.body)
        instructions = data.get("instructions")

        if not instructions:
            return Response(
                {"error": "Instructions are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Store the session information
        sessions[session_id] = {
            "instructions": instructions,
        }

        return JsonResponse(
            {
                "session_token": session_id,
            }
        )

    async def get(self, request):
        session_id = request.GET.get("session_id")

        # Check if the session ID exists
        if session_id not in sessions:
            return Response(
                {"error": "Invalid session ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        session_info = sessions[session_id]
        instructions = session_info["instructions"]

        # Generate the response based on the instructions
        # response = infer(instructions)
        async def generate():
            for i in range(10):
                chunk = f"Chunk {i + 1}: This is some generated content."
                print(chunk, flush=True)
                yield f"data: {json.dumps({'content': chunk})}\n\n"
                await asyncio.sleep(0.5)  # Asynchronous sleep
            yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
