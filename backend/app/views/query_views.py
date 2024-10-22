# File: api/views/execute_query.py

import json

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from app.models.workspace import Workspace
from rest_framework import status
from rest_framework.response import Response

from app.models import Block, Notebook


class ExecuteQueryView(APIView):
    @sync_to_async
    def get_current_workspace(self, user):
        return user.current_workspace()

    async def post(self, request, notebook_id, block_id):
        from workflows.hatchet import hatchet

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
        workflow_run = hatchet.client.admin.run_workflow(
            "ExecuteQueryWorkflow",
            {
                "resource_id": resource_id,
                "block_id": block_id,
                "query": query,
            },
        )

        return JsonResponse(
            {
                "workflow_run": str(workflow_run),
            },
            status=status.HTTP_201_CREATED,
        )

    async def get(self, request, workflow_run_id):
        from workflows.hatchet import hatchet

        workflow_run = hatchet.client.admin.get_workflow_run(workflow_run_id)
        result = await workflow_run.result()
        return JsonResponse(result, status=status.HTTP_200_OK)


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
        user_id = request.user.id
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
                "dbt_resource_id": str(details["dbt_resource"].id),
                "dbt_sql": query,
                "use_fast_compile": False,
            },
        )
        try:
            result = await workflow_run.result()
            signed_url = result.get("dbt_query_preview", {}).get("signed_url", "")
        except Exception as e:
            print(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(
            {"signed_url": signed_url},
            status=status.HTTP_201_CREATED,
        )
