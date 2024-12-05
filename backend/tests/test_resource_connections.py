from app.models import Resource
from app.utils.test_utils import require_env_vars


def dialect_test_contents(resource: Resource, is_db: bool = True):
    dh = resource.details.test_datahub_connection()
    assert dh["success"], dh

    if is_db:
        db = resource.details.test_db_connection()
        assert db["success"], db

    return True


def test_postgres_connection(local_postgres: Resource):
    assert dialect_test_contents(local_postgres)


def test_metabase_connection(local_metabase: Resource):
    assert dialect_test_contents(local_metabase, is_db=False)


@require_env_vars("BIGQUERY_0_WORKSPACE_ID")
def test_bigquery_connection(remote_bigquery: Resource):
    assert dialect_test_contents(remote_bigquery)


@require_env_vars("SNOWFLAKE_0_WORKSPACE_ID")
def test_snowflake_connection(remote_snowflake: Resource):
    assert dialect_test_contents(remote_snowflake)


@require_env_vars("DATABRICKS_0_WORKSPACE_ID")
def test_databricks_connection(remote_databricks: Resource):
    assert dialect_test_contents(remote_databricks)


@require_env_vars("REDSHIFT_0_WORKSPACE_ID")
def test_redshift_connection(remote_redshift: Resource):
    assert dialect_test_contents(remote_redshift)


@require_env_vars("TABLEAU_0_USERNAME")
def test_tableau_connection(remote_tableau: Resource):
    assert dialect_test_contents(remote_tableau, is_db=False)
