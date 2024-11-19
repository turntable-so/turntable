from django_celery_results.models import TaskResult
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import DBTOrchestratorSerializer, TaskSerializer
from app.models.workflows import DBTOrchestrator


class JobViewSet(viewsets.ModelViewSet):
    def create(self, request):
        serializer = DBTOrchestratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        current_orchestrator = DBTOrchestrator.objects.get(id=pk)
        serializer = DBTOrchestratorSerializer(
            instance=current_orchestrator, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        workspace = request.user.current_workspace()
        data = DBTOrchestrator.objects.filter(workspace=workspace)
        serializer = DBTOrchestratorSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return Response(
            DBTOrchestrator.objects.get(id=pk).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        DBTOrchestrator.objects.get(id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        data = DBTOrchestrator.objects.get(id=pk).schedule_now()
        serializer = DBTOrchestratorSerializer(data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class RunViewSet(viewsets.ModelViewSet):
    def list(self, request):
        workspace = request.user.current_workspace()
        dbtresource_id = request.query_params.get("dbtresource_id")
        data = DBTOrchestrator.get_results(
            workspace_id=workspace.id, dbtresource_id=dbtresource_id
        )
        serializer = TaskSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        data = TaskResult.objects.get(task_id=pk)
        serializer = TaskSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        # TODO: implement retry
        pass
