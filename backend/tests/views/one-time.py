import django
from django.conf import settings
from rest_framework.test import APIClient

django.setup()

if __name__ == "__main__":
    from app.models import DBTResource, User

    settings.ALLOWED_HOSTS = ["*"]
    client = APIClient()
    client.force_authenticate(user=User.objects.get(email="accounts@turntable.so"))

    workspace_id = 1
    resource = DBTResource.objects.get(workspace_id=workspace_id)
    resource_data = {
        "workspace_id": workspace_id,
        "dbtresource_id": resource.id,
    }

    commands = ["dbt deps", "dbt parse", "dbt run"]

    BASE_DATA = {
        "commands": commands,
        "cron_str": "*/1 * * * *",
        "name": "test-1",
    }

    BASE_DATA_2 = {
        "commands": commands,
        "cron_str": "*/2 * * * *",
        "name": "test-2",
    }

    BASE_DATA_3 = {
        "commands": commands,
        "cron_str": "*/3 * * * *",
        "name": "test-3",
    }

    BASE_DATA_4 = {
        "commands": commands,
        "cron_str": "*/4 * * * *",
        "name": "test-4",
    }

    BASE_DATA_5 = {
        "commands": commands,
        "cron_str": "*/5 * * * *",
        "name": "test-5",
    }

    BASE_DATA_6 = {
        "commands": commands,
        "cron_str": "*/6 * * * *",
        "name": "test-6",
    }

    for data in [
        BASE_DATA,
        BASE_DATA_2,
        BASE_DATA_3,
        BASE_DATA_4,
        BASE_DATA_5,
        BASE_DATA_6,
    ]:
        data = {**resource_data, **data}
        client.post("/jobs/", data, format="json")
