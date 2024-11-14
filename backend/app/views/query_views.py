from adrf.views import APIView
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from sqlfmt.api import Mode, format_string
from sqlfmt.exception import SqlfmtError

from app.workflows.query import execute_query, validate_query


def make_signed_url_response(result):
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


class QueryPreviewInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    limit = serializers.IntegerField(required=False, default=1000)


class QueryPreviewView(APIView):
    def post(self, request):
        workspace = request.user.current_workspace()
        dbt_resource = workspace.get_dbt_dev_details()

        serializer = QueryPreviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = (
            execute_query.si(
                workspace_id=str(workspace.id),
                resource_id=str(dbt_resource.resource.id),
                sql=serializer.validated_data.get("query"),
                limit=serializer.validated_data.get("limit"),
            )
            .apply_async()
            .get()
        )
        return make_signed_url_response(result)


class QueryValidateInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)


class QueryValidateView(APIView):
    def post(self, request):
        workspace = request.user.current_workspace()
        dbt_resource = workspace.get_dbt_dev_details()

        serializer = QueryValidateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = (
            validate_query.si(
                workspace_id=str(workspace.id),
                resource_id=str(dbt_resource.resource.id),
                sql=serializer.validated_data.get("query"),
            )
            .apply_async()
            .get()
        )
        return JsonResponse(result)


class DbtQueryPreviewInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    use_fast_compile = serializers.BooleanField(required=False, default=True)
    project_id = serializers.CharField(required=True)
    limit = serializers.IntegerField(required=False, default=1000)


class DbtQueryPreviewView(APIView):
    def post(self, request):
        workspace = request.user.current_workspace()
        dbt_resource = workspace.get_dbt_dev_details()
        serializer = DbtQueryPreviewInputSerializer(data=request.data)
        serializer.is_valid()

        with dbt_resource.dbt_repo_context(
            project_id=serializer.validated_data.get("project_id"), isolate=False
        ) as (
            dbtproj,
            project_path,
            _,
        ):
            try:
                sql = None
                if serializer.validated_data.get("use_fast_compile"):
                    sql = dbtproj.fast_compile(serializer.validated_data.get("query"))
                if sql is None:
                    sql = dbtproj.preview(
                        serializer.validated_data.get("query"),
                        data=False,
                    )
                # # TODO: hacky way to catch errors from dbt
            # # we'll eventually need a more robust system for handling this
            except Exception as e:
                ## TODO: this is hacky, we'll eventually want a more robust error handling solution
                if "Compilation Error" in str(e):
                    error_message = str(e).split("Compilation Error")[1].strip()
                    return Response(
                        {"error": error_message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    raise e

            try:
                result = (
                    execute_query.si(
                        workspace_id=str(workspace.id),
                        resource_id=str(dbt_resource.resource.id),
                        sql=sql,
                        limit=serializer.validated_data.get("limit"),
                    )
                    .apply_async()
                    .get()
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return make_signed_url_response(result)


class DbtQueryValidateInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    project_id = serializers.CharField(required=True)
    use_fast_compile = serializers.BooleanField(required=False, default=True)
    limit = serializers.IntegerField(required=False, default=1000)


class DbtQueryValidateView(APIView):
    def post(self, request):
        workspace = request.user.current_workspace()
        dbt_resource = workspace.get_dbt_dev_details()
        serializer = DbtQueryValidateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with dbt_resource.dbt_repo_context(
            project_id=serializer.validated_data.get("project_id"), isolate=False
        ) as (
            dbtproj,
            project_path,
            _,
        ):
            sql = None
            if serializer.validated_data.get("use_fast_compile"):
                sql = dbtproj.fast_compile(serializer.validated_data.get("query"))
            if sql is None:
                sql = dbtproj.preview(
                    serializer.validated_data.get("query"),
                    limit=serializer.validated_data.get("limit"),
                    data=False,
                )

        result = (
            validate_query.si(
                workspace_id=str(workspace.id),
                resource_id=str(dbt_resource.resource.id),
                sql=sql,
            )
            .apply_async()
            .get()
        )
        return JsonResponse(result)


def format_query(query):
    mode = Mode()
    return format_string(query, mode)


class QueryFormatInputSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)


class QueryFormatView(APIView):
    # Note -- accepts dbt or sql
    def post(self, request):
        serializer = QueryFormatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            return JsonResponse(
                {
                    "success": True,
                    "formatted_query": format_query(
                        serializer.validated_data.get("query")
                    ),
                }
            )
        except SqlfmtError:
            return JsonResponse({"success": False})
