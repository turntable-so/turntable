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
        "client_secret": "client",
        "resource_id": test_resource_for_creds.id,
    }
    serializer = LookerDetailsSerializer(data=data)
    assert serializer.is_valid()


def test_creds_are_decrypted_in_python(test_resource_for_creds):
    looker_creds = LookerDetails(
        name="test looker creds",
        base_url="https://looker.com",
        client_id="client_id",
        client_secret="client",
        resource=test_resource_for_creds,
    )
    looker_creds.save()

    creds = LookerDetails.objects.get(id=looker_creds.id)
    assert creds.client_secret == "client"


def test_creds_are_encrypted_in_db(test_resource_for_creds):
    looker_creds = LookerDetails(
        name="test looker creds",
        base_url="https://looker.com",
        client_id="client_id",
        client_secret="client",
        resource=test_resource_for_creds,
    )
    looker_creds.save()
    looker_creds.refresh_from_db()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, encrypted FROM app_resource_details WHERE id = %s",
            [looker_creds.id],
        )
        result = cursor.fetchall()[0]

    assert result[0] == looker_creds.id
    assert "client_secret" not in result[1] and len(result[1]) > 10
