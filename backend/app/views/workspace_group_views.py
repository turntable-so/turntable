from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import WorkspaceDetailSerializer, WorkspaceSerializer
from app.models import WorkspaceGroup, Workspace, User


class WorkspaceGroupViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceGroup.objects.all()
    permission_classes = [AllowAny]

    def list(self, request):
        workspace_groups = WorkspaceGroup.objects.all()
        serializer = WorkspaceSerializer(workspace_groups, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        workspace_group = WorkspaceGroup.objects.get(id=pk)
        serializer = WorkspaceSerializer(workspace_group)
        return Response(serializer.data)

    def create(self, request):
        array_data = request.data["groups"]
        workspace_id = request.data["workspace"]
        workspace = Workspace.objects.get(id=workspace_id)
        for group in array_data:
            user_id = group["user"]
            user = User.objects.get(id=user_id)
            name = group["name"]
            if name == "Admin":
                workspace.add_admin(user)
            else:
                workspace.add_member(user)
        return Response({"status": "success"})
    