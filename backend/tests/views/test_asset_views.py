from django.test import TestCase
from app.models.metadata import Asset
from app.models.resources import Resource
from rest_framework.test import APIClient

from api.serializers import WorkspaceDetailSerializer, WorkspaceSerializer
from app.models import User, Workspace


class WorkspaceViewSetTestCase(TestCase):
    def test_list_workspaces(self):
        resources = Resource.objects.filter(workspace=self.workspace1)
        assets = Asset.objects.filter(resource__in=resources)
