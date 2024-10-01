from hatchet_sdk import Context

from app.models import Resource
from app.models.editor import DBTQuery
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging


@hatchet.workflow(on_events=["dbt_query_preview"], timeout="2m")
@inject_workflow_run_logging(hatchet)
class DBTQueryPreviewWorkflow:
    """
    input structure:
        {
            resource_id: str,
            dbt_resource_id: str | None,
            dbt_sql: str,
            limit: int | None,
            use_fast_compile: bool
        }
    """

    @hatchet.step()
    def dbt_query_preview(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        dbt_sql = context.workflow_input()["dbt_sql"]
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        limit = context.workflow_input().get("limit") or 500
        use_fast_compile = context.workflow_input()["use_fast_compile"]
        resource = Resource.objects.get(id=resource_id)
        dbt_query = DBTQuery(
            dbtresource_id=resource.get_dbt_resource(dbt_resource_id).id,
            dbt_sql=dbt_sql,
            workspace_id=resource.workspace.id,
        )
        if limit:
            return dbt_query.run(use_fast_compile=use_fast_compile, limit=limit)
        return dbt_query.run(use_fast_compile=use_fast_compile)
