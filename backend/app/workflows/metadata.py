import tempfile

from celery import shared_task

from app.core.e2e import DataHubDBParser
from app.models import Resource, ResourceSubtype, Asset, DBTResource, Branch, Column
from ai.documentation.dbt import create_model_description


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
    workunits: int,
    task_id: str | None = None,
):
    resource = Resource.objects.get(id=resource_id)
    resource.details.run_datahub_ingest(
        task_id=self.request.id if not task_id else task_id,
        workunits=workunits,
    )


@shared_task
def process_metadata(workspace_id: str, resource_id: str):
    resource = Resource.objects.get(id=resource_id)
    with resource.datahub_db.open("rb") as f:
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".duckdb") as f2:
            f2.write(f.read())
            parser = DataHubDBParser(resource, f2.name)
            parser.parse()

    DataHubDBParser.combine_and_upload([parser], resource)




@shared_task
def create_single_model_description(workspace_id: str, model_id: str, model_name: str, schema: str, compiled_sql: str) -> None:
    description = create_model_description(
        model_name=model_name,
        schema=schema,
        compiled_sql=compiled_sql,
    )

    model = Asset.objects.get(id=model_id)
    model.ai_description = description.description
    model.save()

@shared_task
def create_model_descriptions(workspace_id: str, resource_id: str) -> list[str]:
    models = (
        Asset.objects.filter(
            workspace_id=workspace_id,
            resource_id=resource_id,
            type=Asset.AssetType.MODEL
        )
    )

    for model in models:
        columns = (
            Column.objects.filter(
                asset_id=model.id
            )
        )

        ## IMPORTANT: Performance note - This will be a big bottleneck.
        ## If we don't run Celery with high concurrency and these requests take
        ## multiple seconds each, this fanout will cause the tasks in the broker to pile
        ## up. Running many threads with `--pool gevent` or `--pool eventlet` can help.
        create_single_model_description.delay(
            workspace_id=workspace_id,
            model_id=model.id,
            model_name=model.name,
            schema="\n".join([column.name + " " + column.type for column in columns]),
            compiled_sql=model.sql,
        )


@shared_task(bind=True)
def sync_metadata(self, workspace_id: str, resource_id: str):
    prepare_dbt_repos(workspace_id=workspace_id, resource_id=resource_id)
    ingest_metadata(
        workspace_id=workspace_id,
        resource_id=resource_id,
        workunits=1000,
        task_id=self.request.id,
    )
    create_model_descriptions(workspace_id=workspace_id, resource_id=resource_id)
    process_metadata(workspace_id=workspace_id, resource_id=resource_id)
