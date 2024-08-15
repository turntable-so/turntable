# File: api/views/execute_query.py


from adrf.views import APIView
from django.http import JsonResponse
from rest_framework import status


class WorkflowViews(APIView):
    async def get(self, request, workflow_run_id):
        from workflows.hatchet import hatchet

        workflow_run = hatchet.client.admin.get_workflow_run(workflow_run_id)
        result = await workflow_run.result()
        return JsonResponse(result, status=status.HTTP_200_OK)
