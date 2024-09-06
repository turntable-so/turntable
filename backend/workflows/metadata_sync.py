import tempfile

from pydantic import create_model
from ai.documentation.dbt import (
    COLUMN_SYSTEM_PROMPT,
    MODEL_SYSTEM_PROMPT,
    ColumnDescription,
    ModelDescription,
)
from app.models.metadata import Asset, Column
from vinyl.lib.enums import AssetType
from hatchet_sdk import Context
import instructor
from django.db import transaction
from app.core.e2e import DataHubDBParser
from app.models import Resource
from app.models.auth import WorkspaceSetting
from app.models.resources import ResourceSubtype
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging
from openai import OpenAI
from anthropic import Anthropic


@hatchet.workflow(on_events=["metadata_sync"], timeout="15m")
@inject_workflow_run_logging(hatchet)
class MetadataSyncWorkflow:
    """
    input structure:
        {
            resource_id: str,
            workunits: Optional[int],
            use_ai: bool
        }
    """

    @hatchet.step(timeout="30m")
    def prepare_dbt_repos(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        for dbt_repo in resource.dbtresource_set.all():
            if dbt_repo.subtype == ResourceSubtype.DBT:
                dbt_repo.upload_artifacts()

    @hatchet.step(timeout="120m", parents=["prepare_dbt_repos"])
    def ingest_metadata(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        workunits = context.workflow_input().get("workunits")
        workflow_run_id = context.workflow_run_id()
        resource.details.run_datahub_ingest(
            workflow_run_id=workflow_run_id, workunits=workunits
        )

    @hatchet.step(timeout="120m", parents=["ingest_metadata"])
    def process_metadata(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        with resource.datahub_db.open("rb") as f:
            with tempfile.NamedTemporaryFile(
                "wb", delete=False, suffix=".duckdb"
            ) as f2:
                f2.write(f.read())
                parser = DataHubDBParser(resource, f2.name)
                parser.parse()

        DataHubDBParser.combine_and_upload([parser], resource)

    @hatchet.step(timeout="120m", parents=["process_metadata"])
    def generate_ai_descriptions(self, context: Context):
        # early return
        # if "use_ai" not in context.workflow_input() or not context.workflow_input()["use_ai"]:
        #     return
        assets = Asset.objects.filter(
            resource__pk=context.workflow_input()["resource_id"], type="model"
        )

        settings = WorkspaceSetting.objects.filter(
            name__in=["aiProvider", "openAiApiKey", "anthropicApiKey"]
        )

        ai_provider_setting = [
            setting for setting in settings if setting.name == "aiProvider"
        ]
        ai_provider_setting = (
            ai_provider_setting[0] if len(ai_provider_setting) != 0 else None
        )

        openai_api_key_setting = [
            setting for setting in settings if setting.name == "openAiApiKey"
        ]
        openai_api_key_setting = (
            openai_api_key_setting[0] if len(openai_api_key_setting) != 0 else None
        )

        anthropic_api_key_setting = [
            setting for setting in settings if setting.name == "anthropicApiKey"
        ]
        anthropic_api_key_setting = (
            anthropic_api_key_setting[0]
            if len(anthropic_api_key_setting) != 0
            else None
        )

        model_defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-opus-20240229",
        }
        model = "gpt-4o-mini"
        if ai_provider_setting is not None:
            model = model_defaults.get(ai_provider_setting.plaintext_value)
        if "model" in context.workflow_input():
            model = context.workflow_input()["model"]
        context.log(model)

        from litellm import completion

        if ai_provider_setting.plaintext_value == "openai":
            client = instructor.from_openai(
                OpenAI(api_key=openai_api_key_setting.secret_value), temperature=0
            )
        elif ai_provider_setting.plaintext_value == "anthropic":
            client = instructor.from_anthropic(
                Anthropic(api_key=anthropic_api_key_setting.secret_value), temperature=0
            )
        else:
            client = instructor.from_litellm(completion, temperature=0)

        for asset in assets:
            columns = Column.objects.filter(asset__pk=asset.id)
            column_map = {col.name: col for col in columns}

            content = create_prompt_content_from_asset(asset, column_map)
            generate_and_set_model_ai_description(client, model, content, asset)

            if len(column_map.keys()) > 15:
                batches = [
                    column_map.keys()[i : i + 15]
                    for i in range(0, len(column_map.keys()), 15)
                ]
            else:
                batches = [column_map.keys()]

            # async/parallel?
            for batch in batches:
                generate_and_set_columns_ai_description(
                    client, model, content, batch, column_map
                )

            # only this needs to be transaction
            @transaction.atomic
            def save():
                asset.save()
                for col in column_map.values():
                    col.save()

            save()


def generate_and_set_model_ai_description(client, model, content, asset):
    resp = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": MODEL_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_model=ModelDescription,
    )
    asset.ai_description = resp.description


def generate_and_set_columns_ai_description(
    client, model, content, column_names, column_map
):
    fields = {f"{k}": (ColumnDescription, ...) for k in column_names}
    ColumnDescriptionModel = create_model("ColumnDescriptionModel", **fields)
    content += "\n\ncolumn_names_to_describe:"
    for colname in column_names:
        content += f"\n- {colname}"

    resp, _ = client.chat.completions.create_with_completion(
        model=model,
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": COLUMN_SYSTEM_PROMPT,
            },
            {"role": "user", "content": content},
        ],
        response_model=ColumnDescriptionModel,
        strict=False,
    )
    for col_name, col_description in resp.model_dump().items():
        column_map.get(col_name).ai_description = col_description["description"]


def create_prompt_content_from_asset(asset: Asset, column_map: dict):
    schema = "\n".join([f"- {k}: {v.type}" for k, v in column_map.items()])
    content = f"model name: {asset.name}\n\n"
    content += f"schema:\n{schema}\n\n"
    content += f"compiled_sql:\n{asset.sql}"
    return content
