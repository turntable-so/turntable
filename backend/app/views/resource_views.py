from adrf.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response

from api.serializers import ResourceSerializer
from app.models.workflows import TASK_START_TIMEOUT, MetadataSyncWorkflow
from app.services.resource_service import ResourceService


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer

    def _get_workspace_and_resource_service(self, request):
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )
        resource_service = ResourceService(workspace=workspace)
        return workspace, resource_service

    def create(self, request):
        workspace, resource_service = self._get_workspace_and_resource_service(request)
        data = request.data
        resource = resource_service.create_resource(data)
        serializer = self.get_serializer(resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        workspace, resource_service = self._get_workspace_and_resource_service(request)
        data = resource_service.list()
        return Response(data)

    def retrieve(self, request, pk=None):
        workspace, resource_service = self._get_workspace_and_resource_service(request)
        data = resource_service.get(resource_id=pk)
        return Response(data)

    def partial_update(self, request, pk=None):
        workspace, resource_service = self._get_workspace_and_resource_service(request)
        data = request.data
        resource = resource_service.partial_update(resource_id=pk, data=data)
        serializer = self.get_serializer(resource)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        workspace, resource_service = self._get_workspace_and_resource_service(request)
        resource_service.delete_resource(resource_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SyncResourceView(APIView):
    def get_current_workspace(self, user):
        return user.current_workspace()

    def post(self, request, resource_id):
        workspace = self.get_current_workspace(request.user)

        workflow = MetadataSyncWorkflow.schedule_now(
            workspace=workspace, resource_id=resource_id
        )

        # wait up to 5 seconds for the task to start
        task_id = workflow.await_next_id(timeout=TASK_START_TIMEOUT)
        if task_id:
            return Response(
                {"detail": "Sync task started."}, status=status.HTTP_202_ACCEPTED
            )


class TestResourceView(APIView):
    def post(self, request, resource_id):
        workspace = request.user.current_workspace()
        resource_service = ResourceService(workspace=workspace)
        test = resource_service.test_resource(resource_id=resource_id)
        return Response(test)
