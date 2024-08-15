# File: api/views/execute_query.py


import json

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from app.models import Block, Notebook


class ExecuteQueryView(APIView):
    @sync_to_async
    def get_current_workspace(self, user):
        return user.workspaces.first()

    async def post(self, request, notebook_id, block_id):
        from workflows.hatchet import hatchet

        workspace = await self.get_current_workspace(request.user)
        data = json.loads(request.body)
        resource_id = data.get("resource_id")
        if not resource_id:
            return Response(
                {"message": "resource_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = data.get("sql")
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
