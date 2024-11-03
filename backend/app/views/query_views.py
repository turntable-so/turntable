# File: api/views/execute_query.py


from adrf.views import APIView
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from app.models.workspace import Workspace
from app.workflows.query import execute_dbt_query, execute_query


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
        signed_url = result.get("signed_url", "")

        if not signed_url:
            return Response(
                {"error": "signed_url not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        if result.get("error"):
            return Response(
                {"error": result.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(
            {"signed_url": signed_url},
            status=status.HTTP_201_CREATED,
        )

    def post(self, request):
        input = self._preprocess(request)
        result = execute_query.si(**input).apply_async().get()
        return self._post_process(result)


class DbtQueryPreviewView(QueryPreviewView):
    def get_current_workspace(self, user):
        return user.current_workspace()

    def get_dbt_details(self, workspace: Workspace):
        return {
            "resource": workspace.get_dbt_details().resource,
            "dbt_resource": workspace.get_dbt_details(),
        }

    def _preprocess(self, request):
        workspace = self.get_current_workspace(request.user)
        query = request.data.get("query")
        if not query:
            return Response(
                {"error": "query required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # assumes a single repo in the workspace for now
        details = self.get_dbt_details(workspace)
        return {
            "resource_id": str(details["resource"].id),
            "workspace_id": str(workspace.id),
            "dbt_resource_id": str(details["dbt_resource"].id),
            "dbt_sql": query,
        }

    def post(self, request):
        input = self._preprocess(request)
        result = execute_dbt_query.si(**input).apply_async().get()
        return self._post_process(result)
