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

    BASE_DATA_2 = {
        "cron_str": "0 18 * * *",
        "commands": ["dbt deps", "dbt parse", "dbt run"],
    }

    def create_job(inp_data):
        data = {**resource_data, **inp_data}
        response = client.post("/jobs/", data, format="json")
        print(response.data, response.status_code)
        scheduled_workflow = DBTOrchestrator.objects.get(id=response.data["id"])
        response = client.post(f"/jobs/{scheduled_workflow.id}/start/")

    create_job(BASE_DATA)
    create_job(BASE_DATA_2)
