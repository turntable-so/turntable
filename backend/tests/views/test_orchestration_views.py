import time

import pytest
import requests
from django.conf import settings
from django_celery_beat.models import PeriodicTask

from app.models.resources import DBTCoreDetails
from app.models.workflows import DBTOrchestrator

BASE_DATA = {
    "cron_str": "0 0 * * *",
    "commands": ["dbt deps", "dbt parse", "dbt run"],
}
MINIMAL_BASE_DATA = {
    "cron_str": "0 0 * * *",
    "commands": ["dbt deps", "dbt parse"],
    "save_artifacts": False,
}
NEW_COMMANDS_DATA = {
    **BASE_DATA,
    "commands": ["dbt deps", "dbt test"],
}

NEW_SCHEDULE_DATA = {
    **BASE_DATA,
    "cron_str": "0 1 * * *",
}


class TestOrchestrationViews:
    @pytest.fixture
    def local_postgres_dbtresource(self, local_postgres):
        return DBTCoreDetails.get_job_dbtresource(
            workspace_id=local_postgres.workspace.id,
            resource_id=local_postgres.id,
        )

    @pytest.fixture
    def resource_data(self, local_postgres_dbtresource):
        return {
            "workspace_id": local_postgres_dbtresource.workspace.id,
            "dbtresource_id": local_postgres_dbtresource.id,
        }

    @pytest.fixture
    def scheduled_workflow(self, client, resource_data):
        data = {**resource_data, **BASE_DATA}
        response = client.post("/jobs/", data, format="json")
        return DBTOrchestrator.objects.get(id=response.data["id"])

    @pytest.fixture
    def minimal_scheduled_workflow(self, client, resource_data):
        data = {**resource_data, **MINIMAL_BASE_DATA}
        response = client.post("/jobs/", data, format="json")
        return DBTOrchestrator.objects.get(id=response.data["id"])

    def test_create_orchestration(self, client, minimal_scheduled_workflow):
        assert minimal_scheduled_workflow is not None
        assert PeriodicTask.objects.count() == 1

    def test_list_orchestration(self, client, minimal_scheduled_workflow):
        response = client.get("/jobs/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert PeriodicTask.objects.count() == 1

    def test_delete_and_restore_orchestration(self, client, minimal_scheduled_workflow):
        orig_periodic_task_id = minimal_scheduled_workflow.periodic_task.id
        response = client.delete(f"/jobs/{minimal_scheduled_workflow.id}/")
        assert response.status_code == 204
        assert PeriodicTask.objects.count() == 0
        assert DBTOrchestrator.objects.count() == 1
        job = DBTOrchestrator.objects.get(id=minimal_scheduled_workflow.id)
        assert job.archived
        assert job.periodic_task is None

        response = client.post(f"/jobs/{minimal_scheduled_workflow.id}/restore/")
        assert PeriodicTask.objects.count() == 1
        assert response.status_code == 204
        assert DBTOrchestrator.objects.count() == 1
        job = DBTOrchestrator.objects.get(id=minimal_scheduled_workflow.id)
        assert not job.archived
        assert job.periodic_task is not None
        assert job.periodic_task.id != orig_periodic_task_id

    @pytest.mark.parametrize(
        "data",
        [NEW_COMMANDS_DATA, NEW_SCHEDULE_DATA],
    )
    def test_update_orchestration(
        self, client, minimal_scheduled_workflow, data, resource_data
    ):
        data = {**resource_data, **data}
        response = client.put(
            f"/jobs/{minimal_scheduled_workflow.id}/", data, format="json"
        )
        assert response.status_code == 200
        assert PeriodicTask.objects.count() == 1
        assert DBTOrchestrator.objects.count() == 1
        assert response.data["cron_str"] == data["cron_str"]
        assert response.data["commands"] == data["commands"]

    def test_invalid_commands(self, client, local_postgres_dbtresource):
        data = {
            **BASE_DATA,
            "workspace_id": local_postgres_dbtresource.workspace.id,
            "dbtresource_id": local_postgres_dbtresource.id,
            "commands": ["not a dbt command"],
        }
        response = client.post("/jobs/", data, format="json")
        assert response.status_code == 400
        assert "All commands must start with 'dbt'" in response.data["commands"]

    def test_orchestration_integration(
        self,
        client,
        custom_celery,
        scheduled_workflow,
        storage,
        local_postgres_dbtresource,
    ):
        time.sleep(1)
        # check start
        response = client.post(f"/jobs/{scheduled_workflow.id}/start/")
        assert response.status_code == 202

        # check result
        workflow = DBTOrchestrator.objects.get(id=response.data["id"])
        _, task_id = workflow.await_next_result()
        assert task_id is not None

        # check runs
        response = client.get("/runs/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        data = response.data["results"][0]
        assert data["task_id"] == task_id
        result = data["result"]
        assert result["success"]
        assert result["run_results"]

        # check subtasks
        response = client.get(f"/runs/{task_id}/")
        assert response.status_code == 200
        data = response.data
        assert data["subtasks"]
        assert len(data["subtasks"]) == 4
        for subtask in data["subtasks"]:
            assert not subtask["subtasks"]

        # check artifacts
        assert data["artifact"]
        url = data["artifact"]["artifact"]
        url = url.replace(settings.AWS_S3_PUBLIC_URL, settings.AWS_S3_ENDPOINT_URL)

        response = requests.get(url)
        assert response.status_code == 200

        # check artifacts export
        local_postgres_dbtresource.refresh_from_db()
        assert local_postgres_dbtresource.exported_manifest
        assert local_postgres_dbtresource.exported_catalog
        assert local_postgres_dbtresource.exported_run_results

    def test_create_webhook_orchestration(self, client, local_postgres_dbtresource):
        data = {
            "workspace_id": local_postgres_dbtresource.workspace.id,
            "dbtresource_id": local_postgres_dbtresource.id,
            "workflow_type": "webhook",
            "hmac_secret_key": "TEST_SECRET_KEY",
            "commands": ["dbt deps", "dbt parse", "dbt run"],
        }
        response = client.post("/jobs/", data, format="json")
        assert response.status_code == 201

    def test_call_webhook_orchestration(
        self, client, custom_celery, local_postgres_dbtresource
    ):
        time.sleep(1)

        secret_key = "TEST_SECRET_KEY"
        data = {
            "workspace_id": local_postgres_dbtresource.workspace.id,
            "dbtresource_id": local_postgres_dbtresource.id,
            "workflow_type": "webhook",
            "hmac_secret_key": secret_key,
            "commands": ["dbt deps", "dbt parse", "dbt run"],
        }
        response = client.post("/jobs/", data, format="json")
        job_id = response.json().get("id")

        # Add signature to headers
        headers = {"X-Signature": f"sha256={'sd'}"}
        response = client.post(
            f"/webhooks/run_job/{job_id}/",
            {
                "event": "run_job"
            },  # Send the original dict, client.post will handle JSON conversion
            format="json",
            **headers,
        )
        assert response.status_code == 201
