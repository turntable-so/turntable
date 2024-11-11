import time

import pytest

from app.models.resources import EnvironmentType
from app.models.workflows import DBTOrchestrator


@pytest.mark.django_db(transaction=True)
def test_orchestration(custom_celery, local_postgres):
    resource = local_postgres
    dbt_resource = resource.dbtresource_set.filter(
        environment=EnvironmentType.PROD
    ).first()

    # ensure the resource is ready
    time.sleep(1)

    resource.refresh_from_db()
    workflow = DBTOrchestrator.schedule_now(
        workspace=resource.workspace,
        resource=resource,
        dbt_resource=dbt_resource,
        commands=["ls", "run"],
        refresh_artifacts=True,
    )
    result = workflow.await_next_result()
    assert result["success"]
    assert all(result["stdouts"])
    assert not any(result["stderrs"])
    assert not result["run_results"][0]
    assert result["run_results"][1]

    dbt_resource.refresh_from_db()
    assert dbt_resource.manifest_json
    assert dbt_resource.catalog_json
    # ensure the workflow is marked completed (used by the UI)
    assert workflow.most_recent(successes_only=True)[0]
