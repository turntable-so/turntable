from hatchet_sdk import Context

from app.models.editor import DBTQuery, Query
from vinyl.lib.utils.query import _QUERY_LIMIT
from workflows.hatchet import hatchet
from workflows.utils.log import inject_workflow_run_logging


@hatchet.workflow(on_events=["query_preview"], timeout="2m")
@inject_workflow_run_logging(hatchet)
class QueryPreviewWorkflow:
    """
    input structure:
        {
            resource_id: str,
            workspace_id: str,
            sql: str,
            limit: int | None,
        }
    """

    @hatchet.step()
    def execute_query(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        workspace_id = context.workflow_input()["workspace_id"]
        sql = context.workflow_input()["sql"]
        if "limit" in context.workflow_input():
            limit = context.workflow_input()["limit"]
        else:
            limit = _QUERY_LIMIT
        query = Query(sql=sql, resource_id=resource_id, workspace_id=workspace_id)
        return query.run(limit=limit)


@hatchet.workflow(on_events=["dbt_query_preview"], timeout="2m")
@inject_workflow_run_logging(hatchet)
class DBTQueryPreviewWorkflow:
    """
    input structure:
        {
            resource_id: str,
            workspace_id: str,
            dbt_resource_id: str | None,
            dbt_sql: str,
            limit: int | None,
            use_fast_compile: bool
        }
    """

    @hatchet.step()
    def execute_query(self, context: Context):
        workspace_id = context.workflow_input()["workspace_id"]
        dbt_sql = context.workflow_input()["dbt_sql"]
        dbt_resource_id = context.workflow_input().get("dbt_resource_id")
        if "limit" in context.workflow_input():
            limit = context.workflow_input()["limit"]
        else:
            limit = _QUERY_LIMIT
        use_fast_compile = context.workflow_input()["use_fast_compile"]
        dbt_query = DBTQuery(
            dbtresource_id=dbt_resource_id,
            dbt_sql=dbt_sql,
            workspace_id=workspace_id,
        )
        return dbt_query.run(use_fast_compile=use_fast_compile, limit=limit)
