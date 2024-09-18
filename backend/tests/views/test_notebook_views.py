import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Notebook, Workspace

User = get_user_model()


@pytest.mark.django_db
class NotebookViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@turntable.so", password="testpass"
        )
        self.client.force_authenticate(user=self.user)
        self.workspace = Workspace.objects.create(name="Test Workspace")
        self.workspace.add_admin(self.user)
        self.workspace.save()
        self.user.save()

    def test_create_notebook(self):
        data = {"title": "New Notebook"}
        response = self.client.post("/notebooks/", data)
        data = {"title": "New Notebook 2"}
        response = self.client.post("/notebooks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notebook.objects.count(), 2)

    def test_update_notebook(self):
        data = {"title": "New Notebook"}
        response = self.client.post("/notebooks/", data)
        data = {
            "title": "Updated notebook",
            "contents": {"paragraph": {"text": "Hello, world!"}},
        }
        response = self.client.put(
            f"/notebooks/{response.data['id']}/", data=data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notebook = Notebook.objects.get(id=response.data["id"])
        self.assertEqual(notebook.contents, data["contents"])

    def test_list_notebooks(self):
        self.client.post("/notebooks/", {"title": "Test Notebook"})
        self.client.post("/notebooks/", {"title": "Test Notebook 2"})
        response = self.client.get("/notebooks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_notebook(self):
        response = self.client.post("/notebooks/", {"title": "Test Notebook"})
        response = self.client.get(f"/notebooks/{response.data['id']}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("workflows.hatchet.hatchet.client.admin.run_workflow")
    @pytest.mark.skip(reason="need to fix")
    def test_execute_query_block(self, mock_run_workflow):
        mock_run_workflow.return_value = {"id": "test-workflow-id"}
        notebook = Notebook.objects.create(workspace=self.workspace)

        block_id = "c8de6eec-d9ae-4cff-b9fd-9e0c250f0de4"

        data = {"resource_id": "test-resource", "sql": "SELECT * FROM test_table"}
        response = self.client.post(
            f"/notebooks/{notebook.id}/blocks/{block_id}/query/",
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("workflow_run", response.json())
        mock_run_workflow.assert_called_once_with(
            "ExecuteQueryWorkflow",
            {
                "resource_id": "test-resource",
                "block_id": block_id,
                "query": "SELECT * FROM test_table",
            },
        )

    def test_notebook_not_found(self):
        response = self.client.get("/notebooks/33652f39-956c-4abb-a58a-d669506d995c/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
