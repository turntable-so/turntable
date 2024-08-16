import pytest
from django.db import connection

from api.serializers import LookerDetailsSerializer
from app.models import LookerDetails, Resource, Workspace

pytestmark = pytest.mark.django_db


@pytest.fixture
def test_resource_for_creds(db) -> Resource:
    workspace = Workspace.objects.create(name="Test Workspace")
    resource = Resource.objects.create(
        name="test resource", type="test", workspace=workspace
    )

    return resource


def test_can_create_looker_creds(test_resource_for_creds):
    looker_creds = LookerDetails(
        name="test looker creds",
        project_path=".",
        base_url="https://looker.com",
        client_id="client_id",
        client_secret="client",
        resource=test_resource_for_creds,
    )
    looker_creds.save()
    looker_creds.refresh_from_db()
    assert LookerDetails.objects.get(id=looker_creds.id)


def test_validate_looker_serializer_missing_field(test_resource_for_creds):
    data = {
        "name": "test looker creds",
        "client_id": "client_id",
        "client_secret": "client",
        "resource": test_resource_for_creds,
    }
    serializer = LookerDetailsSerializer(data=data)
    assert not serializer.is_valid()
    assert serializer.errors["base_url"][0] == "This field is required."


def test_validate_looker_serializer_success(test_resource_for_creds):
    data = {
        "base_url": "https://looker.com",
        "name": "test looker creds",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "resource_id": test_resource_for_creds.id,
    }
    serializer = LookerDetailsSerializer(data=data)
    assert serializer.is_valid()


def test_creds_are_decrypted_in_python(test_resource_for_creds):
    looker_creds = LookerDetails(
        name="test looker creds",
        base_url="https://looker.com",
        client_id="client_id",
        client_secret="client_secret",
        resource=test_resource_for_creds,
        project_path=None,
    )
    looker_creds.save()

    creds = LookerDetails.objects.get(id=looker_creds.id)
    assert creds.client_secret == "client_secret"


def test_creds_are_encrypted_in_db(test_resource_for_creds):
    looker_creds = LookerDetails(
        name="test looker creds",
        base_url="https://looker.com",
        client_id="client_id",
        client_secret="client_secret",
        resource=test_resource_for_creds,
        project_path=None,
    )
    looker_creds.save()
    looker_creds.refresh_from_db()

    with connection.cursor() as cursor:
        cursor.execute("SELECT client_id, client_secret FROM app_lookerdetails")
        result = cursor.fetchone()

    client_id, client_secret = [bytes(val).decode("utf-8") for val in result]
    assert client_id != "client_id"
    assert client_secret != "client_secret"
    assert len(client_id) > 10
    assert len(client_secret) > 10
