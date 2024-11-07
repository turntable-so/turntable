import pytest

from api.serializers import (
    ResourceSerializer,
)
from app.models import Repository, Resource, SSHKey


@pytest.mark.django_db
class TestResourceViews:
    @pytest.fixture
    def ssh_key(self, workspace):
        ssh_key = SSHKey.generate_deploy_key(workspace)
        return ssh_key

    @pytest.fixture
    def resource_id(self, client):
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
        response = client.post("/resources/", data, format="json")
        return response.data["id"]

    def test_list_resources(self, client, workspace):
        Resource.objects.create(name="test resource", workspace=workspace)
        resources = Resource.objects.filter(workspace=workspace)
        assert len(resources) == 1

        serializer = ResourceSerializer(resources, many=True)

        response = client.get("/resources/")
        assert response.status_code == 200
        assert response.data == serializer.data

    def test_create_bigquery_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

    def test_get_bigquery_resource(self, client, resource_id):
        response = client.get(f"/resources/{resource_id}/")
        assert response.status_code == 200
        assert response.data["resource"]["name"] == "Test Resource"
        assert response.data["details"]["service_account"] is not None

    def test_update_bigquery_resource(self, client, resource_id):
        data = {
            "resource": {
                "name": "Test Resource",
            },
        }

        response = client.put(f"/resources/{resource_id}/", data, format="json")

        assert response.status_code == 200
        resource = Resource.objects.get(id=resource_id)
        assert resource.name == "Test Resource"

    def test_update_bigquery_resource_detail(self, client, resource_id):
        data = {
            "config": {
                "service_account": "{ 'new': 'value' }",
            },
        }
        response = client.put(f"/resources/{resource_id}/", data, format="json")

        assert response.status_code == 200
        resource = Resource.objects.get(id=resource_id)
        assert resource.details.service_account == "{ 'new': 'value' }"

    def test_delete_bigquery_resource(self, client, resource_id):
        response = client.delete(f"/resources/{resource_id}/")

        assert response.status_code == 204
        assert not Resource.objects.filter(id=resource_id).exists()

    def test_create_snowflake_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

    def test_get_snowflake_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        resource_id = response.data["id"]

        response = client.get(f"/resources/{resource_id}/")
        assert response.status_code == 200
        assert response.data["resource"]["name"] == "Test Snowflake"
        assert response.data["details"]["account"] is not None

    def test_update_snowflake_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        resource_id = response.data["id"]

        data = {
            "resource": {
                "name": "Test Snowflake",
            },
        }

        response = client.put(f"/resources/{resource_id}/", data, format="json")

        assert response.status_code == 200
        resource = Resource.objects.get(id=resource_id)
        assert resource.name == "Test Snowflake"

    def test_create_postgres_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

    def test_create_dbt_resource(self, client, resource_id, workspace):
        ssh_key = SSHKey.generate_deploy_key(workspace)
        response = client.get("/resources/")
        assert response.status_code == 200
        assert not response.data[-1]["has_dbt"]
        data = {
            "resource": {
                "name": "my dbt project",
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "repository": {
                    "ssh_key": {
                        "id": ssh_key.id,
                        "public_key": ssh_key.public_key,
                    },
                    "git_repo_url": "git@github.com:test/test.git",
                    "main_branch_name": "main",
                },
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

        # should show up in the resource details on the list view
        response = client.get("/resources/")
        assert response.status_code == 200
        assert response.data[-1]["has_dbt"] is True

    def test_create_dbt_resource_get_details(self, client, resource_id, ssh_key):
        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "repository": {
                    "ssh_key": {
                        "id": ssh_key.id,
                        "public_key": ssh_key.public_key,
                    },
                    "git_repo_url": "git@github.com:hello/world.git",
                    "main_branch_name": "main",
                },
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

        resource_id = response.data["id"]
        response = client.get(f"/resources/{resource_id}/")
        assert response.status_code == 200
        assert "dbt_details" in response.data
        assert (
            response.data["dbt_details"]["repository"]["git_repo_url"]
            == "git@github.com:hello/world.git"
        )
        assert "main_branch_name" in response.data["dbt_details"]["repository"].keys()
        assert (
            "public_key" in response.data["dbt_details"]["repository"]["ssh_key"].keys()
        )

    def test_create_dbt_resource_repo_created(self, client, resource_id, ssh_key):
        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "repository": {
                    "ssh_key": {
                        "id": ssh_key.id,
                        "public_key": ssh_key.public_key,
                    },
                    "git_repo_url": "git@github.com:hello/world.git",
                    "main_branch_name": "main",
                },
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

    def test_update_dbt(self, client, resource_id, workspace):
        ssh_key = SSHKey.generate_deploy_key(workspace)
        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "repository": {
                    "ssh_key": {
                        "id": ssh_key.id,
                        "public_key": ssh_key.public_key,
                    },
                    "git_repo_url": "git@github.com:hello/world.git",
                    "main_branch_name": "main",
                },
                "project_path": "/",
                "threads": 1,
                "version": "1.6",
                "database": "test",
                "schema": "test",
            },
        }
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

        data = {
            "resource": {
                "type": "db",
            },
            "subtype": "dbt",
            "config": {
                "resource_id": resource_id,
                "repository": {
                    "ssh_key": {
                        "id": ssh_key.id,
                        "public_key": ssh_key.public_key,
                    },
                    "git_repo_url": "git@github.com:hello/world.git",
                    "main_branch_name": "DIFFERENT",
                },
                "project_path": "/",
                "threads": 1,
                "version": "1.8",
                "database": "test_change",
                "schema": "test_change",
            },
        }
        response = client.put(f"/resources/{resource_id}/", data, format="json")

        response = client.get(f"/resources/{resource_id}/")

        assert response.status_code == 200
        assert response.data["dbt_details"]["version"] == "1.8"
        assert (
            response.data["dbt_details"]["repository"]["git_repo_url"]
            == "git@github.com:hello/world.git"
        )
        assert (
            response.data["dbt_details"]["repository"]["main_branch_name"]
            == "DIFFERENT"
        )

    def test_create_metabase_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

        response = client.get(f"/resources/{response.data['id']}/")
        assert response.status_code == 200
        assert response.data["details"]["connect_uri"] == "http://localhost:4000"

    def test_create_databricks_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201

        response = client.get(f"/resources/{response.data['id']}/")
        assert response.status_code == 200
        assert response.data["details"]["host"] == "test.cloud.databricks.com"

    def test_update_databricks_resource(self, client):
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
        response = client.post("/resources/", data, format="json")
        assert response.status_code == 201
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
        response = client.put(f"/resources/{response.data['id']}/", data, format="json")

        assert response.status_code == 200
        resource = Resource.objects.get(id=response.data["id"])
        assert resource.details.token == "test 2"
