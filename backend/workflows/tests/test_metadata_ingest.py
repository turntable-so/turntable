import pytest

from app.models import Asset, Resource
from conftest import assert_ingest_output
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


@pytest.mark.django_db
def test_metadata_sync(local_metabase, local_postgres, recache: bool):
    resources = [local_metabase, local_postgres]
    # run workflow
    for resource in resources:
        input = {
            "resource_id": resource.id,
        }
        WorkflowDebugger(MetadataSyncWorkflow, input).run()

    # test outputs
    assert_ingest_output(resources)

    # recache datahub_dbs if successful and arg is passed
    if recache:
        for resource in Resource.objects.all():
            if resource.id in [r.id for r in resources]:
                with resource.datahub_db.open("rb") as f:
                    with open(f"fixtures/{resource.datahub_db.name}", "wb") as f2:
                        f2.write(f.read())


@pytest.mark.django_db
def test_limited_metadata_ingest(local_metabase, local_postgres):
    resources = [local_metabase, local_postgres]
    # run workflow
    for resource in resources:
        input = {"resource_id": resource.id, "workunits_limit": 5}
        WorkflowDebugger(MetadataSyncWorkflow, input).run()

    assert Asset.objects.count() > 0
