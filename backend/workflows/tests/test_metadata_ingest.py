import pytest

from app.models import (
    Resource,
)
from app.utils.test_utils import assert_ingest_output, require_env_vars
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


def run_test_sync(resources, recache: bool):
    for resource in resources:
        input = {
            "resource_id": resource.id,
        }
        WorkflowDebugger(MetadataSyncWorkflow, input).run()

    assert_ingest_output(resources)

    # recache datahub_dbs if successful and arg is passed
    if recache:
        for resource in Resource.objects.all():
            if resource.id in [r.id for r in resources]:
                with resource.datahub_db.open("rb") as f:
                    with open(f"fixtures/{resource.datahub_db.name}", "wb") as f2:
                        f2.write(f.read())


@pytest.mark.django_db
def test_metadata_sync(local_metabase, local_postgres, recache: bool):
    resources = [local_metabase, local_postgres]
    run_test_sync(resources, recache)
    assert_ingest_output(resources)


@pytest.mark.django_db
@require_env_vars("BIGQUERY_0_WORKSPACE_ID")
def test_bigquery_sync(remote_bigquery, recache: bool):
    run_test_sync([remote_bigquery], recache)


@pytest.mark.django_db
@require_env_vars("DATABRICKS_0_WORKSPACE_ID")
def test_databricks_sync(remote_databricks, recache: bool):
    run_test_sync([remote_databricks], recache)


@pytest.mark.django_db
@require_env_vars("TABLEAU_0_USERNAME")
def test_tableau_sync(remote_tableau, recache: bool):
    run_test_sync([remote_tableau], recache)
    breakpoint()
