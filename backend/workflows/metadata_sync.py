import tempfile

from hatchet_sdk import Context

from ai.documentation.asset import generate_ai_completions
from app.core.e2e import DataHubDBParser
from app.models import Asset, Resource
from app.models.resources import ResourceSubtype
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging


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
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        ai_provider = resource.workspace.config['ai_provider']
        if ai_provider == 'none':
            return

        api_key = resource.workspace.settings.anthropic_api_key if ai_provider == 'anthropic' else resource.workspace.settings.openai_api_key

        assets = Asset.get_for_resource(resource)

        for asset in assets:
            if asset.type != 'model':
                continue

            generate_ai_completions(asset, ai_provider, api_key)
