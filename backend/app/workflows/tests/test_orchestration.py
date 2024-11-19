import time

import pytest

from app.models.resources import EnvironmentType
from app.models.workflows import DBTOrchestrator


@pytest.mark.django_db(transaction=True)
def test_orchestration(custom_celery, local_postgres):
    resource = local_postgres
    dbtresource = resource.dbtresource_set.filter(
        environment=EnvironmentType.PROD
    ).first()

    # ensure the resource is ready
    time.sleep(1)

    resource.refresh_from_db()
    workflow = DBTOrchestrator(
        workspace=resource.workspace,
        dbtresource=dbtresource,
        commands=["ls", "run"],
        save_artifacts=True,
    ).schedule_now()
    result, _ = workflow.await_next_result()
    assert result["success"]
    assert all(result["stdouts"])
    assert not any(result["stderrs"])
    assert result["run_results"]

    dbtresource.refresh_from_db()
    assert dbtresource.manifest
    assert dbtresource.catalog
    # ensure the workflow is marked completed (used by the UI)
    assert workflow.most_recent(successes_only=True)[0]
