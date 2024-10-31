import pytest

from tasks.orchestration import run_dbt_commands


@pytest.mark.django_db(transaction=True)
def test_orchestration(celery_app, celery_worker, local_postgres):
    resource = local_postgres
    workflow = run_dbt_commands.s(
        resource_id=resource.id,
        dbt_resource_id=resource.dbtresource_set.first().id,
        commands=["ls", "run"],
    )
    result = workflow.apply_async().get()
    assert result["success"]
    assert all(result["stdouts"])
    assert not any(result["stderrs"])
    assert not result["run_results"][0]
    assert result["run_results"][1]
