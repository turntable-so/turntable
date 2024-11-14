import tempfile

from celery import shared_task

from app.core.e2e import DataHubDBParser
from app.models import Resource, ResourceSubtype
from scripts.debug.pyinstrument import pyprofile


@shared_task
def prepare_dbt_repos(workspace_id: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    for dbt_repo in resource.dbtresource_set.all():
        if dbt_repo.subtype == ResourceSubtype.DBT:
            dbt_repo.upload_artifacts()


@shared_task(bind=True)
def ingest_metadata(
    self,
    workspace_id: str,
    resource_id: str,
    workunits: int | None = None,
    task_id: str | None = None,
):
    resource = Resource.objects.get(id=resource_id)
    resource.details.run_datahub_ingest(
        task_id=self.request.id if not task_id else task_id,
        workunits=workunits,
    )


@shared_task
@pyprofile()
def process_metadata(workspace_id: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    with resource.datahub_db.open("rb") as f:
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".duckdb") as f2:
            f2.write(f.read())
            parser = DataHubDBParser(resource, f2.name)
            parser.parse()

    DataHubDBParser.combine_and_upload([parser], resource)


@shared_task(bind=True)
def sync_metadata(self, workspace_id: str, resource_id: str):
    prepare_dbt_repos(workspace_id=workspace_id, resource_id=resource_id)
    ingest_metadata(
        workspace_id=workspace_id,
        resource_id=resource_id,
        task_id=self.request.id,
    )
    process_metadata(workspace_id=workspace_id, resource_id=resource_id)
