import pytest

from workflows.get_lineage import GetLineageWorkflow
from workflows.utils.debug import WorkflowDebugger


@pytest.mark.django_db
def test_get_lineage_workflow(local_postgres):
    input = {
        "resource_id": local_postgres.id,
        "dbt_node_ids": ["model.jaffle_shop.orders"],
        "predecessor_depth": 1,
        "successor_depth": 1,
    }
    res = WorkflowDebugger(GetLineageWorkflow, input).run().result()
    breakpoint()
