from django.test import TestCase
from rest_framework.test import APIClient
from app.models import User
from app.models import Workspace
from api.serializers import WorkspaceSerializer, WorkspaceDetailSerializer


class AssetViewSetTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_assets(self):
        assert 1 == 2

    def test_list_assets_with_resource_id(self):
        assert 1 == 2

    def test_list_assets_with_invalid_resource_id(self):
        assert 1 == 2
