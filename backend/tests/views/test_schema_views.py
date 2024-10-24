import pytest

from app.utils.test_utils import require_env_vars
from tests.views.test_query_views import _validate_query_test


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet")
class TestResourceSchemaView:
    _colnames = ["TABLE_CATALOG", "TABLE_SCHEMA", "TABLE_NAME", "TABLE_TYPE"]

    def _test(
        self,
        client,
        user,
        resource,
        endpoint="/schema/resource/",
        min_rows: int = 10,
    ):
        user.save()
        response = client.post(f"{endpoint}{resource.id}/")
        data = _validate_query_test(response, min_rows)
        colnames = [c.upper() for c in data["column_types"]]
        assert set(colnames) == set(self._colnames)

    def test_resource_schema_postgres(self, client, user, local_postgres):
        self._test(client, user, local_postgres)

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_resource_schema_redshift(self, client, user, remote_redshift):
        self._test(client, user, remote_redshift)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_resource_schema_bigquery(self, client, user, remote_bigquery):
        self._test(client, user, remote_bigquery)

    @require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
    def test_resource_schema_snowflake(self, client, user, remote_snowflake):
        self._test(client, user, remote_snowflake)

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_resource_schema_databricks(self, client, user, remote_databricks):
        self._test(client, user, remote_databricks)


@pytest.mark.django_db
@pytest.mark.usefixtures("force_isolate", "bypass_hatchet")
class TestTableSchemaView:
    _colnames = [
        "TABLE_CATALOG",
        "TABLE_SCHEMA",
        "TABLE_NAME",
        "COLUMN_NAME",
        "ORDINAL_POSITION",
        "DATA_TYPE",
    ]

    def _test(
        self,
        client,
        user,
        resource,
        endpoint="/schema/table/",
        min_rows: int = 1,
    ):
        user.save()
        dbtdetails = resource.dbtresource_set.first()
        response = client.post(
            f"{endpoint}{resource.id}/",
            {
                "database": dbtdetails.database,
                "schema": dbtdetails.schema,
                "table": "customers",
            },
        )
        data = _validate_query_test(response, min_rows)
        colnames = [c.upper() for c in data["column_types"]]
        assert set(colnames) == set(self._colnames)

    def test_table_schema_postgres(self, client, user, local_postgres):
        self._test(client, user, local_postgres)

    @require_env_vars("REDSHIFT_0_WORKSPACE_ID")
    def test_table_schema_redshift(self, client, user, remote_redshift):
        self._test(client, user, remote_redshift)

    @require_env_vars("BIGQUERY_0_WORKSPACE_ID")
    def test_table_schema_bigquery(self, client, user, remote_bigquery):
        self._test(client, user, remote_bigquery)

    @require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
    def test_table_schema_snowflake(self, client, user, remote_snowflake):
        self._test(client, user, remote_snowflake)

    @require_env_vars("DATABRICKS_0_WORKSPACE_ID")
    def test_table_schema_databricks(self, client, user, remote_databricks):
        self._test(client, user, remote_databricks)
