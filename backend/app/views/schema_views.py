from app.views.query_views import QueryPreviewView
from workflows.execute_query import SchemaWorkflow
from workflows.utils.debug import run_workflow_get_result


class ResourceSchemaView(QueryPreviewView):
    def _preprocess(self, request, resource_id):
        workspace = request.user.current_workspace()

        return {
            "workspace_id": str(workspace.id),
            "resource_id": str(resource_id),
        }

    def post(self, request, resource_id):
        result = run_workflow_get_result(
            SchemaWorkflow, self._preprocess(request, resource_id)
        )
        return self._post_process(result)


class TableSchemaView(ResourceSchemaView):
    def _preprocess(self, request, resource_id):
        workspace = request.user.current_workspace()
        database = request.data.get("database", "*")
        schema = request.data.get("schema", "*")
        table = request.data.get("table", "*")
        table_override = f"{database}.{schema}.{table}"
        return {
            "workspace_id": str(workspace.id),
            "resource_id": str(resource_id),
            "with_columns": True,
            "table_override": table_override,
        }
