# File: api/views/execute_query.py

import json

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from app.models import Block, Notebook
from scripts.debug.pyinstrument import pyprofile
from workflows.execute_query import DBTQueryPreviewWorkflow, QueryPreviewWorkflow
from workflows.execute_query_DEPRECATED import ExecuteQueryWorkflow
from workflows.utils.debug import run_workflow_get_result


class NotebookQueryView(APIView):
    @sync_to_async
    def get_current_workspace(self, user):
        return user.current_workspace()

    async def post(self, request, notebook_id, block_id):
        workspace = await self.get_current_workspace(request.user)
        data = json.loads(request.body)
        resource_id = data["resource_id"]
        if not resource_id:
            return Response(
                {"message": "resource_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = data["sql"]
        if not query:
            return Response(
                {"message": "query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            notebook = await Notebook.objects.aget(pk=notebook_id, workspace=workspace)
            block, _ = await Block.objects.aget_or_create(pk=block_id)
        except Notebook.DoesNotExist:
            return Response(
                {"message": f"Notebook of {notebook_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Block.DoesNotExist:
            return Response(
                {"message": f"Block of {block_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Run the async workflow
        workflow_run_id, _ = run_workflow(
            ExecuteQueryWorkflow,
            {
                "resource_id": resource_id,
                "block_id": block_id,
                "query": query,
            },
        )

        return JsonResponse(
            {
                "workflow_run": str(workflow_run_id),
            },
            status=status.HTTP_201_CREATED,
        )

    async def get(self, request, workflow_run_id):
        from workflows.hatchet import hatchet

        workflow_run = hatchet.client.admin.get_workflow_run(workflow_run_id)
        result = await workflow_run.result()
        return JsonResponse(result, status=status.HTTP_200_OK)


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

    @pyprofile()
    def post(self, request):
        result = run_workflow_get_result(
            QueryPreviewWorkflow, self._preprocess(request)
        )
        return self._post_process(result)


class DbtQueryPreviewView(QueryPreviewView):
    def _preprocess(self, request):
        workspace = request.user.current_workspace()
        query = request.data.get("query")
        use_fast_compile = (
            request.query_params.get("use_fast_compile", "true").lower() == "true"
        )
        if not query:
            return Response(
                {"error": "query required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # assumes a single repo in the workspace for now
        details = workspace.get_dbt_details()

        return {
            "workspace_id": str(workspace.id),
            "resource_id": str(details.resource.id),
            "dbt_resource_id": str(details.id),
            "dbt_sql": query,
            "use_fast_compile": use_fast_compile,
        }

    def post(self, request):
        result = run_workflow_get_result(
            DBTQueryPreviewWorkflow, self._preprocess(request)
        )
        return self._post_process(result)
