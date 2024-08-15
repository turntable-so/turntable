import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from app.models import User
from app.models import Resource, Workspace
from django.contrib.auth import get_user_model
from api.serializers import (
    ResourceSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class ResourceViewSetTestCases(TestCase):

    def setUp(self):
        # Set up initial data
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.workspace = Workspace.objects.create(name="Test workspace")
        self.workspace.users.add(self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_resources(self):
        Resource.objects.create(name="test resouce", workspace=self.workspace)
        resources = Resource.objects.filter(workspace=self.workspace)
        assert len(resources) == 1

        serializer = ResourceSerializer(resources, many=True)

        response = self.client.get("/resources/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def _create_resource(self):
        data = {
            "resource": {
                "name": "Test Resource",
                "type": "db",
            },
            "subtype": "bigquery",
            "config": {
                "service_account": "{ 'key': 'value' }",
                "schema_include": ["analytics"],
            },
        }
        response = self.client.post("/resources/", data, format="json")
        return response.data["id"]

    def test_create_bigquery_resource(self):
        data = {
            "resource": {
                "name": "Test Resource",
                "type": "db",
            },
            "subtype": "bigquery",
            "config": {
                "service_account": "{ 'key': 'value' }",
                "schema_include": ["analytics"],
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

    def test_get_bigquery_resource(self):
        resource_id = self._create_resource()

        response = self.client.get(f"/resources/{resource_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["resource"]["name"], "Test Resource")
        self.assertIsNotNone(response.data["details"]["service_account"])

    def test_update_bigquery_resource(self):
        resource_id = self._create_resource()
        data = {
            "resource": {
                "name": "Test Resource",
            },
        }

        response = self.client.patch(f"/resources/{resource_id}/", data, format="json")

        self.assertEqual(response.status_code, 200)
        resource = Resource.objects.get(id=resource_id)
        self.assertEquals(resource.name, "Test Resource")

    def test_update_bigquery_resource_detail(self):
        resource_id = self._create_resource()
        data = {
            "config": {
                "service_account": "{ 'new': 'value' }",
            },
        }
        response = self.client.patch(f"/resources/{resource_id}/", data, format="json")

        self.assertEqual(response.status_code, 200)
        resource = Resource.objects.get(id=resource_id)
        self.assertEquals(resource.details.service_account, "{ 'new': 'value' }")

    def test_delete_bigquery_resource(self):
        resource_id = self._create_resource()

        response = self.client.delete(f"/resources/{resource_id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Resource.objects.filter(id=resource_id).exists())

    def test_create_postgres_resource(self):
        data = {
            "resource": {
                "name": "Test Postgres",
                "type": "db",
            },
            "subtype": "postgres",
            "config": {
                "host": "localhost",
                "port": 5432,
                "database": "test",
                "username": "test",
                "password": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)
