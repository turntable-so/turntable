import pytest
import requests
from django.conf import settings

from app.utils.test_utils import require_env_vars


def _validate_query_test(response):
    assert response.status_code == 201
    data = response.json()
    url = data["signed_url"]
    assert url is not None

    # check signed url data
    url = url.replace(settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL)
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 100


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("force_isolate", "custom_celery")
class TestQueryViews:
    def _test(
        self,
        client,
        user,
        resource,
        endpoint="/query/sql/",
        query="select * from mydb.dbt_sl_test.customers",
    ):
        user.active_workspace_id = resource.workspace.id
        user.save()
        response = client.post(endpoint, {"query": query})
        _validate_query_test(response)

    def test_sql_query_postgres(self, client, user, local_postgres):
        self._test(client, user, local_postgres)

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_sql_query_redshift(self, client, user, remote_redshift):
        self._test(client, user, remote_redshift)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_sql_query_bigquery(self, client, user, remote_bigquery):
        self._test(
            client, user, remote_bigquery, query="select * from dbt_sl_test.customers"
        )  # override query due to bq syntax

    @require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
    def test_sql_query_snowflake(self, client, user, remote_snowflake):
        self._test(client, user, remote_snowflake)

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_sql_query_databricks(self, client, user, remote_databricks):
        self._test(client, user, remote_databricks)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("force_isolate", "custom_celery")
class TestDBTQueryViews:
    @classmethod
    def _test(
        cls,
        client,
        user,
        resource,
        endpoint="/query/dbt/",
        query="select * from {{ ref('customers') }}",
    ):
        user.active_workspace_id = resource.workspace.id
        user.save()
        project_id = resource.dbtresource_set.first().repository.main_branch.id

        response = client.post(
            endpoint,
            {"query": query, "project_id": project_id, "use_fast_compile": True},
        )
        _validate_query_test(response)

    def test_dbt_query_postgres(self, client, user, local_postgres):
        self._test(client, user, local_postgres)

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_dbt_query_redshift(self, client, user, remote_redshift):
        self._test(client, user, remote_redshift)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_dbt_query_bigquery(self, client, user, remote_bigquery):
        self._test(client, user, remote_bigquery)

    @require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
    def test_dbt_query_snowflake(self, client, user, remote_snowflake):
        self._test(
            client,
            user,
            remote_snowflake,
        )

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_dbt_query_databricks(self, client, user, remote_databricks):
        self._test(client, user, remote_databricks)


FORMAT_QUERY = """with source as (select * from {{ source('ecom', 'raw_customers') }}), renamed as (select id as customer_id, name as customer_name from source) select * from renamed"""


@pytest.mark.django_db
def test_format_query(client):
    response = client.post(
        "/query/format/",
        {"query": FORMAT_QUERY},
    )
    out = response.json()
    assert out["success"]
    assert out["formatted_query"] != FORMAT_QUERY
    assert FORMAT_QUERY.count("\n") == 0
    assert out["formatted_query"].count("\n") == 5
