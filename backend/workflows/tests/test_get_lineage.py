import pytest

from workflows.get_lineage import GetLineageWorkflow
from workflows.utils.debug import WorkflowDebugger


@pytest.mark.django_db
def test_get_lineage_workflow(local_postgres):
    input = {
        "resource_id": local_postgres.id,
        "dbt_file_path": "models/marts/customer360/orders.sql",
        "predecessor_depth": 1,
        "successor_depth": 1,
    }
    lineage, asset_errors = (
        WorkflowDebugger(GetLineageWorkflow, input).run().result()["get_lineage_step"]
    )
    assert lineage.columns[0].asset_id == "model.jaffle_shop.stg_orders"
    assert len(lineage.assets) > 0
    assert len(lineage.columns) > 0
    assert len(lineage.asset_links) > 0
    assert len(lineage.column_links) > 0
    assert len(asset_errors) == 0
