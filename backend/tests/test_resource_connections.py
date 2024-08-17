from app.models import Resource


def test_datahub_connection(local_postgres: Resource, local_metabase: Resource):
    assert local_metabase.details.test_datahub_connection()["success"]
    assert local_postgres.details.test_datahub_connection()["success"]


def test_db_connection(local_postgres: Resource):
    assert local_postgres.details.test_db_connection()["success"]
