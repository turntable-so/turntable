import tempfile

from app.core.e2e import DataHubDBParser
from app.models import Resource
from app.models.resources import ArtifactSource
from app.workflows.utils import chain, task


@task
def prepare_dbt_repos(self, workspace_id: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    for dbt_repo in resource.dbtresource_set.all():
        # only generate artifacts if not already generated from orchestration
        if (
            dbt_repo.artifact_source is None
            or dbt_repo.artifact_source == ArtifactSource.ORCHESTRATION
        ):
            dbt_repo.upload_artifacts(artifact_source=ArtifactSource.METADATA_SYNC)


@task
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


@task
def process_metadata(self, workspace_id: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    with resource.datahub_db.open("rb") as f:
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".duckdb") as f2:
            f2.write(f.read())
            parser = DataHubDBParser(resource, f2.name)
            parser.parse()

    DataHubDBParser.combine_and_upload([parser], resource)


@task
def sync_metadata(self, workspace_id: str, resource_id: str, worker: bool = True):
    # check if artifacts exist and were produced by orchestration run
    task_dict = {
        prepare_dbt_repos: {
            "workspace_id": workspace_id,
            "resource_id": resource_id,
        },
        ingest_metadata: {
            "workspace_id": workspace_id,
            "resource_id": resource_id,
            "task_id": self.request.id,
        },
        process_metadata: {
            "workspace_id": workspace_id,
            "resource_id": resource_id,
        },
    }
    if worker:
        tasks = [t.si(**kwargs) for t, kwargs in task_dict.items()]
        chain(*tasks).apply_async().get()
    else:
        for t, kwargs in task_dict.items():
            t(**kwargs)
