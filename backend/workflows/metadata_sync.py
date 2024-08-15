import tempfile

from hatchet_sdk import Context

from app.core.e2e import DataHubDBParser
from app.models import DBTResourceSubtype, Resource, WorkflowRun
from workflows.hatchet import hatchet


@hatchet.workflow(on_events=["metadata_sync"], timeout="15m")
class MetadataSyncWorkflow:
    """
    input structure:
        {
            resource_id: str,
            use_ai: bool
        }
    """

    @hatchet.step(timeout="15s")
    def create_workflow_run(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        workflow_run_id = context.workflow_run_id()
        workflow_run = WorkflowRun.objects.create(
            id=workflow_run_id, resource=resource, status="RUNNING"
        )
        return {"workflow_run_id": str(workflow_run.id)}

    @hatchet.step(timeout="30m", parents=["create_workflow_run"])
    def prepare_dbt_repos(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        for dbt_repo in resource.dbtresource_set.all():
            if dbt_repo.subtype == DBTResourceSubtype.CORE:
                dbt_repo.upload_artifacts()

    @hatchet.step(timeout="120m", parents=["prepare_dbt_repos"])
    def ingest_metadata(self, context: Context):
        resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
        resource.details.run_datahub_ingest()

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

    @hatchet.step(timeout="15s", parents=["process_metadata"])
    def mark_workflow_run_success(self, context: Context):
        workflow_run_id = context.workflow_run_id()
        workflow_run = WorkflowRun.objects.get(id=workflow_run_id)
        workflow_run.status = "SUCCESS"
        workflow_run.save()

    @hatchet.on_failure_step()
    def on_failure(self, context: Context):
        workflow_run_id = context.workflow_run_id()
        workflow_run = WorkflowRun.objects.get(id=workflow_run_id)
        workflow_run.status = "FAILED"
        workflow_run.save()
