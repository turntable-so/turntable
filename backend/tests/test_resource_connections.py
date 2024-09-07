import pytest

from app.models import Resource
from app.utils.test_utils import require_env_vars


@pytest.mark.django_db
def test_datahub_connection(local_postgres: Resource, local_metabase: Resource):
    mb = local_metabase.details.test_datahub_connection()
    assert mb["success"], mb
    lp = local_postgres.details.test_datahub_connection()
    assert lp["success"], lp


@pytest.mark.django_db
def test_db_connection(local_postgres: Resource):
    lp = local_postgres.details.test_db_connection()
    assert lp["success"], lp


DIALECT_DICT = {
    "BIGQUERY_1_WORKSPACE_ID": {"fixture": "remote_bigquery", "db": True},
    "SNOWFLAKE_1_WORKSPACE_ID": {"fixture": "remote_snowflake", "db": True},
    "DATABRICKS_1_WORKSPACE_ID": {"fixture": "remote_databricks", "db": True},
}


def dialect_test_contents(resource: Resource, is_db: bool = True):
    dh = resource.details.test_datahub_connection()
    assert dh["success"], dh

    if is_db:
        db = resource.details.test_db_connection()
        assert db["success"], db

    return True


@pytest.mark.django_db
@require_env_vars("BIGQUERY_1_WORKSPACE_ID")
def test_bigquery_connection(remote_bigquery: Resource):
    assert dialect_test_contents(remote_bigquery)


@pytest.mark.django_db
@require_env_vars("SNOWFLAKE_1_WORKSPACE_ID")
def test_snowflake_connection(remote_snowflake: Resource):
    assert dialect_test_contents(remote_snowflake)


@pytest.mark.django_db
@require_env_vars("DATABRICKS_1_WORKSPACE_ID")
def test_databricks_connection(remote_databricks: Resource):
    assert dialect_test_contents(remote_databricks)


@pytest.mark.django_db
@require_env_vars("TABLEAU_1_USERNAME")
def test_tableau_connection(remote_tableau: Resource):
    assert dialect_test_contents(remote_tableau, is_db=False)
