import django
from django.conf import settings

from rest_framework.test import APIClient


django.setup()

if __name__ == "__main__":
    from app.models.workflows import DBTOrchestrator
    from app.models import User, DBTResource

    settings.ALLOWED_HOSTS = ["*"]
    client = APIClient()
    client.force_authenticate(user=User.objects.get(email="accounts@turntable.so"))

    workspace_id = 1
    resource = DBTResource.objects.get(workspace_id=workspace_id)
    resource_data = {
        "workspace_id": workspace_id,
        "dbtresource_id": resource.id,
    }

    BASE_DATA = {
        "cron_str": "0 0 * * *",
        "commands": ["dbt deps", "dbt parse", "dbt run"],
    }

    data = {**resource_data, **BASE_DATA}
    response = client.post("/jobs/", data, format="json")
    print(response.data, response.status_code)
    scheduled_workflow = DBTOrchestrator.objects.get(id=response.data["id"])
    response = client.post(f"/jobs/{scheduled_workflow.id}/start/")
    workflow = DBTOrchestrator.objects.get(id=response.data["id"])
    # _, task_id = workflow.await_next_result()
    # response = client.get(f"/runs/{task_id}/")
