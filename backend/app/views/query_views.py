# File: api/views/execute_query.py

import json

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from app.models.workspace import Workspace
from rest_framework import status
from rest_framework.response import Response

from app.models import Block, Notebook
from workflows.execute_query import DBTQueryPreviewWorkflow, QueryPreviewWorkflow
from workflows.execute_query_DEPRECATED import ExecuteQueryWorkflow
from workflows.utils.debug import run_workflow_get_result


class QueryPreviewView(APIView):
    def _preprocess(self, request):
        workspace = request.user.current_workspace()
        query = request.data.get("query")
        if not query:
            return Response(
                {"error": "query required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # assumes a single repo in the workspace for now
        dbt_resource = workspace.get_dbt_details()

        return {
            "workspace_id": str(workspace.id),
            "resource_id": str(dbt_resource.resource.id),
            "sql": query,
        }

    def _post_process(self, result):
        signed_url = result.get("execute_query", {}).get("signed_url", "")

        if not signed_url:
            return Response(
                {"error": "signed_url not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {"signed_url": signed_url},
            status=status.HTTP_201_CREATED,
        )

    def post(self, request):
        result = run_workflow_get_result(
            QueryPreviewWorkflow, self._preprocess(request)
        )
        return self._post_process(result)


class DbtQueryPreviewView(APIView):

    @sync_to_async
    def get_current_workspace(self, user):
        return user.current_workspace()

    @sync_to_async
    def get_dbt_details(self, workspace: Workspace):
        return {
            "resource": workspace.get_dbt_details().resource,
            "dbt_resource": workspace.get_dbt_details(),
        }

    async def post(self, request):
        from workflows.hatchet import hatchet

        workspace = await self.get_current_workspace(request.user)
        query = request.data.get("query")
        if not query:
            return Response(
                {"error": "query required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # assumes a single repo in the workspace for now
        details = await self.get_dbt_details(workspace)

        workflow_run = hatchet.client.admin.run_workflow(
            "DBTQueryPreviewWorkflow",
            {
                "resource_id": str(details["resource"].id),
                "workspace_id": str(workspace.id),
                "dbt_resource_id": str(details["dbt_resource"].id),
                "dbt_sql": query,
                "use_fast_compile": False,
            },
        )

        result = await workflow_run.result()
        workflow_result = result.get("execute_query")
        if workflow_result.get("error"):
            return Response(
                {"error": workflow_result.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        signed_url = workflow_result.get("signed_url")
        if not signed_url:
            return Response(
                {"error": "signed_url not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        return JsonResponse(
            {"signed_url": signed_url},
            status=status.HTTP_201_CREATED,
        )
