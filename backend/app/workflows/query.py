from celery import shared_task

from app.models.query import DBTQuery, Query
from vinyl.lib.utils.query import _QUERY_LIMIT


@shared_task
def execute_query(workspace_id, resource_id, sql, limit=None):
    limit = _QUERY_LIMIT if limit is None else limit
    query = Query(sql=sql, resource_id=resource_id, workspace_id=workspace_id)
    return query.run(limit=limit)


@shared_task
def execute_dbt_query(
    workspace_id, dbt_resource_id, dbt_sql, limit=None, use_fast_compile=True
):
    limit = _QUERY_LIMIT if limit is None else limit
    query = DBTQuery(
        dbtresource_id=dbt_resource_id,
        dbt_sql=dbt_sql,
        workspace_id=workspace_id,
    )
    return query.run(use_fast_compile=use_fast_compile, limit=limit)
