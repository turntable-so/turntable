from app.models.query import DBTQuery, Query
from app.workflows.utils import task
from vinyl.lib.utils.query import _QUERY_LIMIT


@task
def execute_query(self, workspace_id, resource_id, sql, limit=None):
    limit = _QUERY_LIMIT if limit is None else limit
    query = Query.objects.create(
        sql=sql, resource_id=resource_id, workspace_id=workspace_id
    )
    return query.run(limit=limit)


@task
def validate_query(self, workspace_id, resource_id, sql):
    query = Query.objects.create(
        sql=sql, resource_id=resource_id, workspace_id=workspace_id
    )
    return query.validate()


@task
def execute_dbt_query(
    self, workspace_id, dbt_resource_id, dbt_sql, limit=None, use_fast_compile=True
):
    limit = _QUERY_LIMIT if limit is None else limit
    query = DBTQuery(
        dbtresource_id=dbt_resource_id,
        dbt_sql=dbt_sql,
        workspace_id=workspace_id,
    )
    return query.run(use_fast_compile=use_fast_compile, limit=limit)
