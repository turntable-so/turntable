import pytest
import requests
from django.conf import settings

from app.models import Resource
from app.utils.test_utils import require_env_vars
from app.workflows.query import execute_dbt_query, execute_query

TEST_QUERY = "select * from mydb.dbt_sl_test.raw_products"

TEST_DBT_QUERY = "select * from {{ ref('raw_products') }}"


def run_test_query(
    resource: Resource,
    query=TEST_QUERY,
    limit=10,
):
    result = (
        execute_query.si(
            workspace_id=str(resource.workspace.id),
            resource_id=str(resource.id),
            sql=query,
            limit=limit,
        )
        .apply_async()
        .get()
    )
    url = result["signed_url"].replace(
        settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL
    )
    data = requests.get(url)
    assert data.status_code == 200
    assert len(data.json()["data"]) == limit


def run_test_dbt_query(
    resource: Resource,
    query=TEST_DBT_QUERY,
    use_fast_compile: bool = True,
    output_len=10,
):
    dbtresource = resource.dbtresource_set.first()
    result = (
        execute_dbt_query.si(
            workspace_id=str(resource.workspace.id),
            dbt_resource_id=str(dbtresource.id),
            dbt_sql=query,
            use_fast_compile=use_fast_compile,
        )
        .apply_async()
        .get()
    )
    url = result["signed_url"].replace(
        settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL
    )
    data = requests.get(url)
    assert data.status_code == 200
    assert len(data.json()["data"]) == output_len


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("custom_celery")
class TestQuery:
    def test_query_postgres(self, local_postgres):
        run_test_query(local_postgres)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_query_bigquery(self, remote_bigquery):
        adj_query = TEST_QUERY.replace(
            "mydb", f"`{remote_bigquery.details.service_account['project_id']}`"
        )
        run_test_query(remote_bigquery, query=adj_query)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("custom_celery")
class TestDBTQuery:
    def test_dbt_query_postgres(self, local_postgres):
        run_test_dbt_query(local_postgres)
        run_test_dbt_query(local_postgres, use_fast_compile=False)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_dbt_query_bigquery(self, remote_bigquery):
        run_test_dbt_query(remote_bigquery)
        run_test_dbt_query(remote_bigquery, use_fast_compile=False)
