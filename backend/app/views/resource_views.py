from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import ResourceDetailsSerializer, ResourceSerializer
from app.models.resources import Resource
from app.services.resource_service import ResourceService


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer

    def create(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )
        data = request.data
        resource_service = ResourceService(workspace=workspace)

        resource = resource_service.create_resource(data)
        serializer = self.get_serializer(resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        workspace = request.user.current_workspace()
        resource_service = ResourceService(workspace=workspace)
        data = resource_service.list()
        return Response(data)

    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        resource_service = ResourceService(workspace=workspace)
        data = resource_service.get(resource_id=pk)

        return Response(data)

    def partial_update(self, request, pk=None):
        workspace = request.user.current_workspace()
        resource_service = ResourceService(workspace=workspace)
        data = request.data
        resource = resource_service.partial_update(resource_id=pk, data=data)
        serializer = self.get_serializer(resource)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )
        resource_service = ResourceService(workspace=workspace)
        resource_service.delete_resource(resource_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SyncResourceView(APIView):
    @sync_to_async
    def get_current_workspace(self, user):
        return user.workspaces.first()

    async def post(self, request, resource_id):
        workspace = await self.get_current_workspace(request.user)
        resource_service = ResourceService(workspace=workspace)
        job = await resource_service.sync_resource(resource_id=resource_id)
        if job:
            return Response(
                {"detail": "Sync task started."}, status=status.HTTP_202_ACCEPTED
            )
