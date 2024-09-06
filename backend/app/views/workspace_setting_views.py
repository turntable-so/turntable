from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import WorkspaceSettingSerializer
from app.models import WorkspaceGroup, Workspace, User, WorkspaceSetting


class WorkspaceSettingViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceSetting.objects.all()
    serializer_class = WorkspaceSettingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        return WorkspaceSetting.objects.filter(workspace__users=user)
