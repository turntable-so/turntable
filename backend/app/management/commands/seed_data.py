import os

from django.core.management.base import BaseCommand

from app.models import (
    DBTCoreDetails,
    DBTResourceSubtype,
    MetabaseDetails,
    PostgresDetails,
    Resource,
    ResourceType,
    User,
    Workspace,
)
from vinyl.lib.dbt_methods import DBTVersion
from workflows.metadata_sync import MetadataSyncWorkflow
from workflows.utils.debug import WorkflowDebugger


def local_user():
    user = User.objects.create_user(
        name="Turntable Dev", email="dev@turntable.so", password="mypassword"
    )
    return user


def local_workspace(user):
    # create turntable full
    workspace = Workspace.objects.create(
        id="org_2XVt0EheumDcoCerhQzcUlVmXvG",
        name="Parkers Vinyl Shop",
    )
    workspace.add_admin(user)
    workspace.save()
    return workspace


def local_postgres(workspace):
    resource = Resource.objects.create(
        workspace=workspace, name="Test Postgres Resource", type=ResourceType.DB
    )
    PostgresDetails(
        resource=resource,
        host=os.getenv("POSTGRES_TEST_DB_HOST", "postgres_test_db"),
        port=os.getenv("POSTGRES_TEST_DB_PORT", 5432),
        database="mydb",
        username="myuser",
        password="mypassword",
    ).save()

    DBTCoreDetails(
        resource=resource,
        project_path="fixtures/test_resources/jaffle_shop",
        threads=1,
        version=DBTVersion.V1_7.value,
        subtype=DBTResourceSubtype.CORE,
        database="mydb",
        schema="dbt_sl_test",
    ).save()

    return resource


def local_metabase(workspace):
    resource = Resource.objects.create(
        workspace=workspace, name="Test Metabase Resource", type=ResourceType.BI
    )

    MetabaseDetails(
        resource=resource,
        username="test@example.com",
        password="mypassword1",
        connect_uri=os.getenv("TEST_METABASE_URI", "http://metabase:4000"),
    ).save()

    return resource


class Command(BaseCommand):
    help = "Seed data with inital user and workspace"

    def handle(self, *args, **kwargs):
        if User.objects.exists() or Workspace.objects.exists():
            self.stdout.write(
                self.style.WARNING("Data already exists. Skipping seeding.")
            )
            return

        user = local_user()
        workspace = local_workspace(user)
        postgres = local_postgres(workspace)
        metabase = local_metabase(workspace)
        WorkflowDebugger(MetadataSyncWorkflow, {"resource_id": postgres.id}).run()
        WorkflowDebugger(MetadataSyncWorkflow, {"resource_id": metabase.id}).run()

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database"))
