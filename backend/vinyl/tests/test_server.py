import pytest
from fastapi.testclient import TestClient

from vinyl.infra.http_server.server import (
    app,
    get_project,
)
from vinyl.lib.project import Project


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_project] = lambda: Project.bootstrap()
    client = TestClient(app)
    return client


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_query_model(client):
    response = client.get("/models/amount_base?limit=10")
    assert response.status_code == 200


def test_query_metric(client):
    response = client.get("/metrics/fare_metrics?grain=months=1&limit=10")
    assert response.status_code == 200
