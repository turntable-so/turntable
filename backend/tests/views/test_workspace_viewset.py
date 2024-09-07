from django.test import TestCase
from rest_framework.test import APIClient
from app.models import User
from app.models import Workspace
from api.serializers import WorkspaceSerializer, WorkspaceDetailSerializer


class WorkspaceViewSetTestCase(TestCase):

    def setUp(self):
        # Set up initial data
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.workspace1 = Workspace.objects.create(name="Workspace 1")
        self.workspace1.users.add(self.user)
        self.workspace2 = Workspace.objects.create(name="Workspace 2")
        self.workspace2.users.add(self.user)

    def test_list_workspaces(self):
        response = self.client.get("/workspaces/")
        self.assertEqual(response.status_code, 200)
        workspaces = Workspace.objects.filter(users=self.user)
        serializer = WorkspaceSerializer(workspaces, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_workspace(self):
        data = {
            "name": "New Workspace",
        }
        response = self.client.post("/workspaces/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "New Workspace")

    def test_update_workspace(self):
        data = {
            "name": "Updated Workspace",
        }
        response = self.client.put(
            f"/workspaces/{self.workspace1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Updated Workspace")

    def test_retrieve_workspace(self):
        self.user.switch_workspace(self.workspace1)
        response = self.client.get(f"/workspaces/me/")
        self.assertEqual(response.status_code, 200)
        serializer = WorkspaceDetailSerializer(self.workspace1)

        self.assertEqual(response.data, serializer.data)

    def test_switch_workspace(self):
        self.user.switch_workspace(self.workspace1)

        response = self.client.get("/workspaces/me/")
        self.assertEqual(response.data["id"], str(self.workspace1.id))

        data = {
            "workspace_id": self.workspace2.id,
        }

        response = self.client.post(
            "/workspaces/switch_workspace/", data, format="json"
        )

        response = self.client.get("/workspaces/me/")
        self.assertEqual(response.data["id"], str(self.workspace2.id))
