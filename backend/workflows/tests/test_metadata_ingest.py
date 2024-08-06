import pytest

from app.models import (
    Resource,
)
from conftest import assert_ingest_output
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


@pytest.mark.skip
@pytest.mark.nointernal
@pytest.mark.django_db(transaction=True)
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


# def test_already(prepopulated_dev_db):
#     return


# @pytest.mark.django_db
# def test_metadata_sync_internal(bigquery, turntable_dbt, turntable_dbt_mini):
#     resources = [bigquery]
#     for resource in resources:
#         input = {
#             "resource_id": resource.id,
#         }
#         WorkflowDebugger(MetadataSyncWorkflow, input).run()
#         # test outputs
#     assert_ingest_output(resources)


@pytest.mark.django_db
def test_external(capchase):
    resources = capchase[:1]
    for resource in resources:
        input = {
            "resource_id": resource.id,
        }
        WorkflowDebugger(MetadataSyncWorkflow, input).run()
