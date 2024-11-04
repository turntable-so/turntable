import pytest

from app.models.workflows import DBTOrchestrator


@pytest.mark.django_db(transaction=True)
def test_orchestration(custom_celery, local_postgres):
    resource = local_postgres
    resource.refresh_from_db()
    workflow = DBTOrchestrator.schedule_now(
        workspace=resource.workspace,
        resource=resource,
        dbt_resource=resource.dbtresource_set.first(),
        commands=["ls", "run"],
    )
    result = workflow.await_next_result()
    assert result["success"]
    assert all(result["stdouts"])
    assert not any(result["stderrs"])
    assert not result["run_results"][0]
    assert result["run_results"][1]
