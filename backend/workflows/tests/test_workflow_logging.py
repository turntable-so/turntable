import pytest
from hatchet_sdk import Context

from app.models import Resource, WorkflowRun
from workflows.hatchet import hatchet
from workflows.utils.debug import WorkflowDebugger
from workflows.utils.log import inject_workflow_run_logging


@pytest.mark.django_db
def test_workflow_success(local_postgres: Resource):
    @inject_workflow_run_logging(hatchet)
    @hatchet.workflow(on_events=["test_sync"], timeout="1m")
    class TestWorkflow:
        @hatchet.step(timeout="30s")
        def step1(self, context: Context):
            pass

    WorkflowDebugger(TestWorkflow, {"resource_id": local_postgres.id}).run()
    assert WorkflowRun.objects.count() == 1


@pytest.mark.django_db
def test_workflow_failure(local_postgres):
    @inject_workflow_run_logging(hatchet)
    @hatchet.workflow(on_events=["test_sync"], timeout="1m")
    class TestWorkflow:
        @hatchet.step(timeout="30s")
        def step1(self, context: Context):
            raise ValueError("test")

    with pytest.raises(ValueError):
        WorkflowDebugger(TestWorkflow, {"resource_id": local_postgres.id}).run()
    assert WorkflowRun.objects.count() == 1
    assert WorkflowRun.objects.first().status == "FAILED"
