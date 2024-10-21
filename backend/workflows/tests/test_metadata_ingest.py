import pandas as pd
import pytest
from mpire import WorkerPool

from app.models import (
    Resource,
)
from app.utils.test_utils import assert_ingest_output, require_env_vars
from scripts.debug.pyinstrument import pyprofile
from vinyl.lib.table import VinylTable
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import ContextDebugger, WorkflowDebugger


def run_test_sync(
    resources, recache: bool, use_cache: bool = False, db_read_path: str | None = None
):
    for resource in resources:
        input = {
            "resource_id": resource.id,
        }
        if use_cache:
            if db_read_path is None:
                db_read_path = f"fixtures/datahub_dbs/{resource.details.subtype}.duckdb"
            with open(db_read_path, "rb") as f:
                resource.datahub_db.save(db_read_path, f, save=True)
            MetadataSyncWorkflow().process_metadata(ContextDebugger({"input": input}))
        else:
            WorkflowDebugger(MetadataSyncWorkflow, input).run()

    breakpoint()

    assert_ingest_output(resources)

    # recache datahub_dbs if successful and arg is passed
    if recache:
        for resource in Resource.objects.all():
            if resource.id in [r.id for r in resources]:
                with resource.datahub_db.open("rb") as f:
                    db_save_path = (
                        f"fixtures/datahub_dbs/{resource.details.subtype}.duckdb"
                    )
                    with open(db_save_path, "wb") as f2:
                        f2.write(f.read())


@pytest.mark.django_db
def test_metadata_sync(local_metabase, local_postgres, recache: bool, use_cache: bool):
    resources = [local_metabase, local_postgres]
    run_test_sync(resources, recache, use_cache)
    assert_ingest_output(resources)


@pytest.mark.django_db
@require_env_vars("BIGQUERY_0_WORKSPACE_ID")
def test_bigquery_sync(remote_bigquery, recache: bool, use_cache: bool):
    run_test_sync([remote_bigquery], recache, use_cache)


@pytest.mark.django_db
@require_env_vars("DATABRICKS_0_WORKSPACE_ID")
def test_databricks_sync(remote_databricks, recache: bool, use_cache: bool):
    run_test_sync([remote_databricks], recache, use_cache)


@pytest.mark.django_db
@require_env_vars("REDSHIFT_0_WORKSPACE_ID")
def test_redshift_sync(remote_redshift, recache: bool, use_cache: bool):
    run_test_sync([remote_redshift], recache, use_cache)


@pytest.mark.django_db
@require_env_vars("TABLEAU_0_USERNAME")
def test_tableau_sync(remote_tableau, recache: bool, use_cache: bool):
    run_test_sync([remote_tableau], recache, use_cache)


@pytest.mark.django_db
def test_eda(local_postgres):
    connector = local_postgres.details.get_connector()
    conn = connector._connect()
    table = VinylTable(conn.table("orders", database="dbt_sl_test")._arg)
    breakpoint()


# @pytest.mark.django_db
# @pyprofile()
# def test_edb(local_postgres):
#     connector = local_postgres.details.get_connector()
#     table = connector._get_table(database="mydb", schema="dbt_sl_test", table="orders")
#     vinyltable = VinylTable(table._arg)

#     def get_sql(tbl, col):
#         return tbl.eda(
#             cols=[col],
#             topk=20,
#         )

#     sqls = [
#         vinyltable.eda(cols=[col], topk=20).to_sql(
#             dialect="postgres", node_name="", optimized=True
#         )
#         for col in table.columns
#     ]
#     with WorkerPool(n_jobs=30, start_method="threading", use_dill=True) as pool:
#         dfs = pool.imap(connector.sql_to_df, sqls)
#     df = pd.concat(dfs)
#     df.reset_index(drop=True)
#     df.sort_values(by="position", inplace=True)
#     print(df)


@pytest.mark.django_db
@pyprofile()
def test_edb(internal_bigquery):
    connector = internal_bigquery.details.get_connector()
    table = connector._get_table(
        database="analytics-dev-372514", schema="posthog", table="event"
    )
    vinyltable = VinylTable(table._arg)

    def get_sql(tbl, col):
        return tbl.eda(
            cols=[col],
            topk=20,
        )

    sqls = [
        vinyltable.eda(cols=[col], topk=20).to_sql(dialect="bigquery", node_name="")
        for col in table.columns
    ]
    with WorkerPool(n_jobs=10, start_method="threading", use_dill=True) as pool:
        dfs = pool.imap(connector.sql_to_df, sqls)
    df = pd.concat(dfs)
    df.reset_index(drop=True)
    df.sort_values(by="position", inplace=True)
    print(df)
