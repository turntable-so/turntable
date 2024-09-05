import pytest

from app.models import Resource


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
