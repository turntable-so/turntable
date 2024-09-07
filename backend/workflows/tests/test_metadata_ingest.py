import pytest

from app.models import (
    Resource,
)
from app.utils.test_utils import assert_ingest_output, require_env_vars
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
@require_env_vars("DATABRICKS_1_WORKSPACE_ID")
def test_databricks_metadata_sync(remote_databricks):
    input = {
        "resource_id": remote_databricks.id,
    }
    WorkflowDebugger(MetadataSyncWorkflow, input).run()
    assert_ingest_output([remote_databricks])


@pytest.mark.django_db
@require_env_vars("TABLEAU_1_USERNAME")
def test_tableau_metadata_sync(remote_tableau):
    input = {
        "resource_id": remote_tableau.id,
    }
    WorkflowDebugger(MetadataSyncWorkflow, input).run()
    assert_ingest_output([remote_tableau])
