# File: api/views/execute_query.py


from adrf.views import APIView
from celery.result import AsyncResult
from django.http import JsonResponse
from rest_framework import status


class WorkflowViews(APIView):
    async def get(self, request, workflow_run_id):
        result = AsyncResult(workflow_run_id).get()
        return JsonResponse(result, status=status.HTTP_200_OK)
