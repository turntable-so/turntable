# File: api/views/execute_query.py

import asyncio

from django.http import JsonResponse
from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from workflows.hatchet import hatchet


class WorkflowViews(APIView):
    async def get(self, request, workflow_run_id):
        workflow_run = hatchet.client.admin.get_workflow_run(workflow_run_id)
        result = await workflow_run.result()
        return JsonResponse(result, status=status.HTTP_200_OK)
