import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from api.serializers import (
    ResourceSerializer,
)
from app.models import Resource, User, Workspace

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
        self.assertEqual(resource.name, "Test Resource")

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
        self.assertEqual(resource.details.service_account, "{ 'new': 'value' }")

    def test_delete_bigquery_resource(self):
        resource_id = self._create_resource()

        response = self.client.delete(f"/resources/{resource_id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Resource.objects.filter(id=resource_id).exists())

    def test_create_snowflake_resource(self):
        data = {
            "resource": {
                "name": "Test Snowflake",
                "type": "db",
            },
            "subtype": "snowflake",
            "config": {
                "account": "test",
                "username": "test",
                "password": "test",
                "warehouse": "test",
                "schema": "test",
                "role": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

    def test_get_snowflake_resource(self):
        data = {
            "resource": {
                "name": "Test Snowflake",
                "type": "db",
            },
            "subtype": "snowflake",
            "config": {
                "account": "test",
                "username": "test",
                "password": "test",
                "warehouse": "test",
                "schema": "test",
                "role": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        resource_id = response.data["id"]

        response = self.client.get(f"/resources/{resource_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["resource"]["name"], "Test Snowflake")
        self.assertIsNotNone(response.data["details"]["account"])

    def test_update_snowflake_resource(self):
        data = {
            "resource": {
                "name": "Test Snowflake",
                "type": "db",
            },
            "subtype": "snowflake",
            "config": {
                "account": "test",
                "username": "test",
                "password": "test",
                "warehouse": "test",
                "schema": "test",
                "role": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        resource_id = response.data["id"]

        data = {
            "resource": {
                "name": "Test Snowflake",
            },
        }

        response = self.client.patch(f"/resources/{resource_id}/", data, format="json")

        self.assertEqual(response.status_code, 200)
        resource = Resource.objects.get(id=resource_id)
        self.assertEqual(resource.name, "Test Snowflake")

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

    def test_create_dbt_resource(self):
        resource_id = self._create_resource()
        response = self.client.get("/resources/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["has_dbt"], False)
        data = {
            "resource": {
                "name": "my dbt project",
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "git_repo_url": "git@github.com:turntable-so/dbt.git",
                "main_git_branch": "main",
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

        # should show up in the resource details on the list view
        response = self.client.get("/resources/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["has_dbt"], True)

    def test_create_dbt_resource_get_details(self):
        resource_id = self._create_resource()
        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "git_repo_url": "git@github.com:turntable-so/dbt.git",
                "main_git_branch": "main",
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

        resource_id = response.data["id"]
        response = self.client.get(f"/resources/{resource_id}/")
        self.assertContains(response, "dbt_details", status_code=200)

    def test_update_dbt(self):
        resource_id = self._create_resource()
        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "git_repo_url": "git@github.com:turntable-so/dbt.git",
                "main_git_branch": "main",
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

        data = {
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "deploy_key": "ssh-key",
                "git_repo_url": "git@github.com:turntable-so/dbt.git",
                "main_git_branch": "main",
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }

        response = self.client.patch(f"/resources/{resource_id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        resource = Resource.objects.get(id=resource_id)
        self.assertEqual(resource.name, "Test Resource")

    def test_create_metabase_resource(self):
        data = {
            "resource": {
                "name": "Test Metabase",
                "type": "bi",
            },
            "subtype": "metabase",
            "config": {
                "connect_uri": "http://localhost:4000",
                "username": "test",
                "password": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

        response = self.client.get(f"/resources/{response.data['id']}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["details"]["connect_uri"], "http://localhost:4000"
        )

    def test_create_databricks_resource(self):
        data = {
            "resource": {
                "name": "Test Databricks",
                "type": "db",
            },
            "subtype": "databricks",
            "config": {
                "host": "test.cloud.databricks.com",
                "http_path": "/sql/1.0/warehouses/test",
                "token": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)

        response = self.client.get(f"/resources/{response.data['id']}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["details"]["host"], "test.cloud.databricks.com")

    def test_update_databricks_resource(self):
        data = {
            "resource": {
                "name": "Test Databricks",
                "type": "db",
            },
            "subtype": "databricks",
            "config": {
                "host": "test.cloud.databricks.com",
                "http_path": "/sql/1.0/warehouses/test",
                "token": "test",
            },
        }
        response = self.client.post("/resources/", data, format="json")
        self.assertContains(response, "id", status_code=201)
        data = {
            "resource": {
                "name": "Test Databricks",
                "type": "db",
            },
            "config": {
                "host": "test.cloud.databricks.com",
                "http_path": "/sql/1.0/warehouses/test",
                "token": "test 2",
            },
        }
        response = self.client.patch(
            f"/resources/{response.data['id']}/", data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        resource = Resource.objects.get(id=response.data["id"])
        self.assertEqual(resource.details.token, "test 2")
