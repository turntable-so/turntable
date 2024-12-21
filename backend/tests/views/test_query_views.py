import pytest
import requests
from django.conf import settings

from app.utils.test_utils import require_env_vars


@pytest.mark.usefixtures("force_isolate", "custom_celery", "storage")
class BaseQueryTest:
    endpoint = None
    default_query = None
    query_edits = {}
    success_options = [True]

    def _build_query(self, resource, success=True):
        return self.query_edits.get(resource.subtype, self.default_query)

    def _test(self, client, user, resource, limit=None, success=True, **kwargs):
        user.active_workspace_id = resource.workspace.id
        user.save()

        data = {
            "query": self._build_query(resource, success),
            **kwargs,
        }
        if limit is not None:
            data["limit"] = limit

        response = client.post(self.endpoint, data)
        return self._validate_response(response, limit, success)

    def _validate_response(self, response, limit, success):
        assert response.status_code == 201
        data = response.json()

        url = data["signed_url"]
        assert url is not None

        # check signed url data
        url = url.replace(settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL)
        response = requests.get(url)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 100
        if limit is not None:
            assert len(data) <= limit

        return url

    @pytest.mark.parametrize("limit", [None, 100])
    @pytest.mark.xdist_group(name="postgres")
    def test_postgres(self, request, client, user, local_postgres, limit, success):
        self._test(
            client,
            user,
            local_postgres,
            limit=limit,
            success=success,
        )

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_redshift(self, client, user, remote_redshift, success):
        self._test(client, user, remote_redshift, success=success)

    @require_env_vars("CLICKHOUSE_0_WORKSPACE_ID")
    def test_clickhouse(self, client, user, remote_clickhouse, success):
        self._test(client, user, remote_clickhouse, success=success)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_bigquery(self, client, user, remote_bigquery, success):
        self._test(client, user, remote_bigquery, success=success)

    @require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
    def test_snowflake(self, client, user, remote_snowflake, success):
        self._test(client, user, remote_snowflake, success=success)

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_databricks(self, client, user, remote_databricks, success):
        self._test(client, user, remote_databricks, success=success)


@pytest.mark.parametrize("success", [True])
class TestQueryViews(BaseQueryTest):
    endpoint = "/query/sql/"
    default_query = "select * from mydb.dbt_sl_test.customers"
    query_edits = {
        "clickhouse": "select * from dbt_sl_test.customers",
        "bigquery": "select * from dbt_sl_test.customers",
    }


class TestDBTQueryViews(TestQueryViews):
    endpoint = "/query/dbt/"
    default_query = "select * from {{ ref('customers') }}"
    query_edits = {}

    def _test(self, client, user, resource, query=None, limit=None, success=True):
        project_id = resource.dbtresource_set.first().repository.main_project.id
        super()._test(
            client,
            user,
            resource,
            limit=limit,
            project_id=project_id,
            use_fast_compile=True,
            success=success,
        )


@pytest.mark.parametrize("success", [True, False])
class TestValidateViews(BaseQueryTest):
    endpoint = "/validate/sql/"
    default_query = TestQueryViews.default_query
    query_edits = TestQueryViews.query_edits

    def _build_query(self, resource, success=True):
        out = super()._build_query(resource, success)
        # add a random character to the query if it should fail
        return out if success else out + "x"

    def _validate_response(self, response, limit, success):
        assert response.status_code == 200
        assert response.json()["status"] == "success" if success else "error"


class TestValidateDBTViews(TestValidateViews):
    endpoint = "/validate/dbt/"
    default_query = TestDBTQueryViews.default_query
    query_edits = TestDBTQueryViews.query_edits

    def _test(self, client, user, resource, query=None, limit=None, success=True):
        project_id = resource.dbtresource_set.first().repository.main_project.id
        super()._test(
            client,
            user,
            resource,
            limit=limit,
            project_id=project_id,
            use_fast_compile=True,
            success=success,
        )


FORMAT_QUERY = """with source as (select * from {{ source('ecom', 'raw_customers') }}), renamed as (select id as customer_id, name as customer_name from source) select * from renamed"""


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
