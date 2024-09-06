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


@pytest.mark.django_db
@require_env_vars("DATABRICKS_1_WORKSPACE_ID")
def test_databricks_connection(remote_databricks: Resource):
    dh = remote_databricks.details.test_datahub_connection()
    assert dh["success"], dh

    db = remote_databricks.details.test_db_connection()
    assert db["success"], db
