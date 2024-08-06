from django.core.management.base import BaseCommand

from app.models import (
    DBTCoreDetails,
    DBTResourceSubtype,
    MetabaseDetails,
    PostgresDetails,
    Resource,
    ResourceType,
    Workspace,
)
from vinyl.lib.dbt_methods import DBTVersion


class Command(BaseCommand):
    help = "Seed lineage data"

    def handle(self, *args, **kwargs):
        workspace = Workspace.objects.get(id="7dffaaff-9463-4fd8-ac10-180243f729f3")

        metabase_resource = Resource.objects.create(
            workspace=workspace, name="Test Metabase Resource", type=ResourceType.BI
        )

        postgres_resource = Resource.objects.create(
            workspace=workspace, name="Test Postgres Resource", type=ResourceType.DB
        )

        MetabaseDetails(
            resource=metabase_resource,
            username="test@example.com",
            password="mypassword1",
            connect_uri="http://metabase:4000",
        ).save()

        PostgresDetails(
            resource=postgres_resource,
            host="postgres_test_db",
            port=5432,
            database="mydb",
            username="myuser",
            password="mypassword",
        ).save()

        DBTCoreDetails(
            resource=postgres_resource,
            project_path="fixtures/test_resources/jaffle_shop",
            threads=1,
            version=DBTVersion.V1_7.value,
            subtype=DBTResourceSubtype.CORE,
            database="mydb",
            schema="dbt_sl_test",
        ).save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
