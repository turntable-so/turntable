from django.db.models import OuterRef, Subquery
from django_celery_results.models import TaskResult
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.serializers import (
    DBTCoreDetailsSerializer,
    DBTOrchestratorSerializer,
    TaskResultSerializer,
    TaskResultWithJobSerializer,
)
from app.models.resources import DBTCoreDetails
from app.models.workflows import DBTOrchestrator


class Pagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class JobViewSet(viewsets.ModelViewSet):
    def create(self, request):
        workspace = request.user.current_workspace()
        serializer = DBTOrchestratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        workspace = request.user.current_workspace()
        current_orchestrator = DBTOrchestrator.objects.get(id=pk)
        serializer = DBTOrchestratorSerializer(
            instance=current_orchestrator, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        workspace = request.user.current_workspace()

        latest_task_subquery = (
            TaskResult.objects.filter(
                periodic_task_name=OuterRef("replacement_identifier")
            )
            .order_by("-date_done")
            .values("date_done")[:1]
        )
        queryset = (
            DBTOrchestrator.objects.filter(workspace=workspace, crontab__isnull=False)
            .annotate(latest_date_done=Subquery(latest_task_subquery))
            .order_by("-latest_date_done")
        )

        paginator = Pagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = DBTOrchestratorSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"])
    def environments(self, request):
        workspace = request.user.current_workspace()
        environments = DBTCoreDetails.objects.filter(workspace=workspace)
        serializer = DBTCoreDetailsSerializer(environments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        data = DBTOrchestrator.objects.get(id=pk)
        serializer = DBTOrchestratorSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        DBTOrchestrator.objects.get(id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        data = DBTOrchestrator.objects.get(id=pk).schedule_now()
        serializer = DBTOrchestratorSerializer(data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"])
    def runs(self, request, pk=None):
        job = DBTOrchestrator.objects.get(id=pk)
        queryset = job.most_recent(n=None)
        paginator = Pagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = TaskResultSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        job = DBTOrchestrator.objects.get(id=pk)

        n = 100
        total_runs_queryset = job.most_recent(n=n)
        total_runs = total_runs_queryset.count()

        succeeded_runs_queryset = job.most_recent(n=n, successes_only=True)
        succeeded_runs = succeeded_runs_queryset.count()

        errored_runs_queryset = job.most_recent(n=n, failures_only=True)
        errored_runs = errored_runs_queryset.count()

        success_rate = (succeeded_runs / total_runs) * 100 if total_runs > 0 else 0
        rounded_success_rate = int(round(success_rate, 0))

        data = {
            "success_rate": rounded_success_rate,
            "completed": total_runs,
            "succeeded": succeeded_runs,
            "errored": errored_runs,
        }
        return Response(data, status=status.HTTP_200_OK)


class RunViewSet(viewsets.ModelViewSet):
    def list(self, request):
        workspace = request.user.current_workspace()
        dbtresource_id = request.query_params.get("dbtresource_id")
        data = DBTOrchestrator.get_results_with_filters(
            workspace_id=workspace.id, dbtresource_id=dbtresource_id
        )
        paginator = Pagination()
        paginated_data = paginator.paginate_queryset(data, request)
        serializer = TaskResultWithJobSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        data = TaskResult.objects.get(task_id=pk)
        serializer = TaskResultSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        # TODO: implement retry
        pass
