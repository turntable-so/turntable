import pytest
import requests
from django.conf import settings

from app.models import Resource
from app.utils.test_utils import require_env_vars
from workflows.execute_query_DEPRECATED import ExecuteQueryWorkflow
from workflows.utils.debug import WorkflowDebugger

TEST_QUERY = "select * from mydb.dbt_sl_test.raw_products"

TEST_DBT_QUERY_FAST = "select * from {{ ref('raw_products') }}"


def run_test_query(resource: Resource, user, query=TEST_QUERY, output_len=10):
    input = {
        "resource_id": resource.id,
        "block_id": "c8de6eec-d9ae-4cff-b9fd-9e0c250f0de4",
        "query": query,
    }
    result = WorkflowDebugger(ExecuteQueryWorkflow, input).run().result()
    url = result["execute_query"]["signed_url"].replace(
        settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL
    )

    data = requests.get(url)
    assert data.status_code == 200
    assert len(data.json()["data"]) == output_len


@pytest.mark.django_db
def test_query_local(local_postgres, user):
    run_test_query(local_postgres, user)


@pytest.mark.django_db
@require_env_vars("DATABRICKS_0_WORKSPACE_ID")
def test_query_databricks(remote_databricks, user):
    run_test_query(remote_databricks, user)


@pytest.mark.django_db
@require_env_vars("BIGQUERY_0_WORKSPACE_ID")
def test_query_bigquery(remote_bigquery, user):
    run_test_query(remote_bigquery, user)
