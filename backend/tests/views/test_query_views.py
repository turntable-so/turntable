import pytest
import requests
from django.conf import settings

from app.utils.test_utils import require_env_vars
from app.utils.url import build_url


def _validate_query_test(response, min_rows: int = 100):
    assert response.status_code == 201
    data = response.json()
    url = data["signed_url"]
    assert url is not None

    # check signed url data
    url = url.replace(settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL)
    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= min_rows
    return data


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet")
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


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet")
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

        endpoint = build_url(endpoint, {"use_fast_compile": True})

        response = client.post(endpoint, {"query": query})
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
