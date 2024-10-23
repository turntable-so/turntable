import pytest
import requests
from django.conf import settings

from app.utils.test_utils import require_env_vars
from app.utils.url import build_url


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet")
class TestQueryViews:
    @property
    def _test_query(self):
        return "select * from {{ ref('customers') }}"

    @classmethod
    def _query_preview_test_helper(cls, client, user, resource, endpoint, query):
        user.active_workspace_id = resource.workspace.id
        user.save()

        endpoint = build_url(endpoint, {"use_fast_compile": True})

        response = client.post(endpoint, {"query": query})
        assert response.status_code == 201
        data = response.json()
        url = data["signed_url"]
        assert url is not None

        # check signed url data
        url = url.replace(settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL)
        response = requests.get(url)
        assert response.status_code == 200
        breakpoint()
        assert len(response.json()["data"]) >= 100

    def test_dbt_query_preview_postgres(self, client, user, local_postgres):
        self._query_preview_test_helper(
            client, user, local_postgres, "/query/preview/", self._test_query
        )

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_dbt_query_preview_redshift(self, client, user, remote_redshift):
        self._query_preview_test_helper(
            client, user, remote_redshift, "/query/preview/", self._test_query
        )

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_dbt_query_preview_bigquery(self, client, user, remote_bigquery):
        self._query_preview_test_helper(
            client, user, remote_bigquery, "/query/preview/", self._test_query
        )

    @require_env_vars("SNOWFLAKE_1_WORKSPACE_ID")
    def test_dbt_query_preview_snowflake(self, client, user, remote_snowflake):
        self._query_preview_test_helper(
            client,
            user,
            remote_snowflake,
            "/query/preview/",
        )

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_dbt_query_preview_databricks(self, client, user, remote_databricks):
        self._query_preview_test_helper(
            client, user, remote_databricks, "/query/preview/", self._test_query
        )
