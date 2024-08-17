import pytest

from app.models import WorkflowRun
from workflows.dbt_runner import DBTRunnerWorkflow
from workflows.utils.debug import WorkflowDebugger


@pytest.mark.django_db
def test_dbt_runner_success(local_postgres):
    input = {
        "resource_id": local_postgres.id,
        "commands": ["test", "run"],
    }
    res = WorkflowDebugger(DBTRunnerWorkflow, input).run().result()["run_dbt_commands"]
    assert res["success"]
    assert all(res["stdouts"])
    assert all(res["stderrs"])
    assert all(res["run_results"])
    assert WorkflowRun.objects.count() == 1
    assert WorkflowRun.objects.first().status == "SUCCESS"


@pytest.mark.django_db
def test_dbt_runner_failure(local_postgres):
    input = {"resource_id": local_postgres.id, "commands": ["run -z"]}
    res = WorkflowDebugger(DBTRunnerWorkflow, input).run().result()["run_dbt_commands"]

    assert not res["success"]
    assert not all(res["stdouts"])
    assert all(res["stderrs"])
    assert not all(res["run_results"])
    assert WorkflowRun.objects.count() == 1
    assert WorkflowRun.objects.first().status == "SUCCESS"
