from hatchet_sdk import Context

from app.models.editor import DBTQuery, Query
from app.models.resources import Resource
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


@hatchet.workflow(on_events=["table_schema"], timeout="4m")
@inject_workflow_run_logging(hatchet)
class SchemaWorkflow:
    """
    input structure:
        {
            resource_id: str,
            workspace_id: str,
            with_columns: bool,
            table_override: str | None,
        }
    """

    @hatchet.step()
    def execute_query(self, context: Context):
        resource_id = context.workflow_input()["resource_id"]
        workspace_id = context.workflow_input()["workspace_id"]
        with_columns = context.workflow_input().get("with_columns", False)
        table_override = context.workflow_input().get("table_override")
        resource = Resource.objects.get(id=resource_id)

        if not hasattr(resource.details, "get_connector"):
            raise ValueError("Resource does not have a connector")
        connector = resource.details.get_connector()
        query_ast = connector._get_information_schema_query(
            table_override=table_override, with_columns=with_columns
        )
        query = Query(
            sql=query_ast.sql(dialect=resource.details.subtype),
            resource_id=resource_id,
            workspace_id=workspace_id,
        )
        return query.run()
