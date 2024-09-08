import os
from typing import List

import instructor
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel

from app.models.metadata import Asset, Column

class AssetDescription(BaseModel):
    description: str

class ColumnDescription(BaseModel):
    description: str

ASSET_SYSTEM_PROMPT = """
Instructions:
- You are an expert AI data analyst.
- Given a database model's name, schema, and underlying sql, write a description for that model.

Rules:
- Respond in a few paragraphs.
- Use clear language.
- Explain the purpose of the model and how it can be used in real-world applications.
- Highlight the significant patterns and correlations that can be discovered in the data, as well as any key features.
- Avoid first-person language like "we" and "us".
- Where applicable, use analogies or examples to clarify any technical terms or concepts.
"""

COLUMN_SYSTEM_PROMPT = """
Instructions:
- You are an expert AI data analyst.
- Given a database model's name, underlying sql, and a specific column and column type, write a clear and concise description for that column.

Rules:
- Describe the purpose and meaning of the column, including any unique details or logic that would be useful for review.
- Ensure that your descriptions are informative and help stakeholders understand the model's data in an straightforward manner.
- Use plain language that is accessible to all stakeholders
- Avoid complex technical jargon
- Don't start your description with filler works like "This column is used to..." or "This column represents...". Just describe the column directly.
- Use analogies or examples where necessary to clarify technical terms or concepts.
"""

def get_ai_client(ai_provider):
    if ai_provider == 'openai':
        return instructor.from_openai(OpenAI(api_key=os.environ.get("OPENAI_API_KEY")))

    if ai_provider == 'anthropic':
        return instructor.from_anthropic(Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")))

    raise Exception(f"Unknown AI provider: {ai_provider}")

def get_ai_model(ai_provider):
    if ai_provider == 'openai':
        return "gpt-4o"
    if ai_provider == 'anthropic':
        return "claude-3-5-sonnet-20240620"
    raise Exception(f"Unknown AI provider: {ai_provider}")


def generate_ai_completions(asset: Asset, ai_provider='openai'):
    client = get_ai_client(ai_provider)
    ai_model = get_ai_model(ai_provider)
    columns = asset.columns.all()

    generate_asset_completion(client, ai_model, asset, columns)
    generate_column_descriptions(client, ai_model, columns)


def generate_asset_completion(client, ai_model: str, asset: Asset, columns: List[Column]):
    content = f"model name: {asset.name}\n\n"
    content += "schema:\n" + "\n".join([f"- {name}: {type}" for name, type in columns.values_list("name", "type")])
    content += f"\n\nsql:\n{asset.sql}"

    resp = client.chat.completions.create(
        model=ai_model,
        messages=[
            {
                "role": "system",
                "content": ASSET_SYSTEM_PROMPT,
            },
            {"role": "user", "content": content},
        ],
        response_model=AssetDescription,
    )

    asset.ai_description = resp.description
    asset.save()

def generate_column_descriptions(client, ai_model: str, columns: List[Column]):
    for column in columns:
        content = f"model name: {column.asset.name}\n\n"
        content += f"column name: {column.name}\n\n"
        content += f"column type: {column.type}\n\n"
        content += f"\n\nsql:\n{column.asset.sql}"

        resp = client.chat.completions.create(
            model=ai_model,
            messages=[
                {
                    "role": "system",
                    "content": COLUMN_SYSTEM_PROMPT,
                },
                {"role": "user", "content": content},
            ],
            response_model=ColumnDescription,
        )

        column.ai_description = resp.description
        column.save()
