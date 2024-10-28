import pytest
import requests
from django.conf import settings

from app.models import Resource
from app.utils.test_utils import require_env_vars
from workflows.execute_query import DBTQueryPreviewWorkflow
from workflows.utils.debug import WorkflowDebugger

TEST_QUERY = "select * from mydb.dbt_sl_test.raw_products"

TEST_DBT_QUERY = "select * from {{ ref('raw_products') }}"


def run_test_dbt_query(
    resource: Resource,
    query=TEST_DBT_QUERY,
    use_fast_compile: bool = True,
    output_len=10,
):
    input = {
        "workspace_id": resource.workspace.id,
        "resource_id": resource.id,
        "dbt_resource_id": resource.get_dbt_resource().id,
        "dbt_sql": query,
        "use_fast_compile": use_fast_compile,
    }
    result = WorkflowDebugger(DBTQueryPreviewWorkflow, input).run().result()
    url = result["execute_query"]["signed_url"].replace(
        settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL
    )
    data = requests.get(url)
    assert data.status_code == 200
    assert len(data.json()["data"]) == output_len


@pytest.mark.django_db
def test_dbt_query_local(local_postgres):
    run_test_dbt_query(local_postgres)
    run_test_dbt_query(local_postgres, use_fast_compile=False)


# @pytest.mark.django_db
# @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
# def test_dbt_query_databricks(remote_databricks, user):
#     run_test_dbt_query(remote_databricks, user)
#     run_test_dbt_query(remote_databricks, user, use_fast_compile=False)


@pytest.mark.django_db
@require_env_vars("BIGQUERY_0_WORKSPACE_ID")
def test_dbt_query_bigquery(remote_bigquery):
    run_test_dbt_query(remote_bigquery)
    run_test_dbt_query(remote_bigquery, use_fast_compile=False)
