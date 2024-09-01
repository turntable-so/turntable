import tempfile

from hatchet_sdk import Context

from app.core.e2e import DataHubDBParser
from app.models import Resource, ResourceSubtype
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
        resource.details.run_datahub_ingest(workunits=workunits)

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
