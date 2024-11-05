# File: api/views/execute_query.py


from adrf.views import APIView
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from app.workflows.query import execute_query


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
    def _preprocess(self, request):
        workspace = request.user.current_workspace()
        query = request.data.get("query")
        if not query:
            return Response(
                {"error": "query required"}, status=status.HTTP_400_BAD_REQUEST
            )
        use_fast_compile = request.data.get("use_fast_compile", True)
        limit = request.data.get("limit")
        branch_id = request.data.get("branch_id")
        dbt_resource = workspace.get_dbt_details()
        with dbt_resource.dbt_repo_context(branch_id) as (dbtproj, project_path, _):
            sql = None
            if use_fast_compile:
                sql = dbtproj.fast_compile(query)
            if sql is None:
                sql = dbtproj.preview(query, limit=limit, data=False)
        return {
            "workspace_id": str(workspace.id),
            "resource_id": str(dbt_resource.resource.id),
            "sql": sql,
        }
