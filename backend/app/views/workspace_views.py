from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from api.serializers import WorkspaceDetailSerializer, WorkspaceSerializer
from app.models import Workspace
import os

minio_host = os.getenv("MINIO_HOST")


class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    permission_classes = [AllowAny]  # Allow access to all users

    def list(self, request):
        user = request.user
        workspaces = Workspace.objects.filter(users=user)
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        workspace = Workspace.objects.create(name=request.data["name"])
        workspace.add_admin(user)

        workspace.save()
        if "icon_file" in request.data:
            workspace.icon_file = request.data["icon_file"]
            workspace.save()  # Save to ensure the file is uploaded
            url = workspace.icon_file.url
            if url.startswith("http://minio:9000/") and minio_host:
                url = url.replace("http://minio:9000/", minio_host)
            workspace.icon_url = url.split("?")[0]
        workspace.save()

        user.switch_workspace(workspace)

        serializer = WorkspaceSerializer(workspace)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        workspace = self.get_object()
        workspace.name = request.data.get("name", workspace.name)
        if "icon_file" in request.data:
            workspace.icon_file = request.data["icon_file"]
            workspace.save()  # Save to ensure the file is uploaded
            url = workspace.icon_file.url
            if url.startswith("http://minio:9000/") and minio_host:
                url = url.replace("http://minio:9000/", minio_host)
            url = url.split("?")[0]
            workspace.icon_url = url

        workspace.save()
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)

    # NOTE: for this endpoint we only return the workspace details for the current user
    # the workspace the user is currently logged into
    # eventually we'll expand this for generic workspace retrieval
    def retrieve(self, request, pk=None):
        user = request.user
        workspace = user.current_workspace()
        serializer = WorkspaceDetailSerializer(
            workspace, context={"request": request}, many=False
        )

        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def switch_workspace(self, request):
        user = request.user
        workspace_id = request.data.get("workspace_id")
        workspace = Workspace.objects.get(id=workspace_id)
        user.switch_workspace(workspace)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)
