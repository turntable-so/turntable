import os

from app.models import (
    DBTCoreDetails,
    MetabaseDetails,
    PostgresDetails,
    Resource,
    ResourceSubtype,
    ResourceType,
    User,
    Workspace,
)
from vinyl.lib.dbt_methods import DBTVersion


def create_local_user():
    name = "Turntable Dev"
    email = "dev@turntable.so"
    password = "mypassword"
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return User.objects.create_user(name=name, email=email, password=password)


def create_local_workspace(user):
    # create turntable full
    try:
        return Workspace.objects.get(id="org_2XVt0EheumDcoCerhQzcUlVmXvG")
    except Workspace.DoesNotExist:
        workspace = Workspace.objects.create(
            id="org_2XVt0EheumDcoCerhQzcUlVmXvG",
            name="Parkers Vinyl Shop",
        )
        workspace.add_admin(user)
        workspace.save()
        return workspace


def create_local_postgres(workspace):
    resource_name = "Test Postgres Resource"
    try:
        resource = Resource.objects.get(
            workspace=workspace, name=resource_name, type=ResourceType.DB
        )
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, name=resource_name, type=ResourceType.DB
        )
        if not hasattr(resource, "details") or not isinstance(
            resource.details, PostgresDetails
        ):
            PostgresDetails(
                resource=resource,
                host=os.getenv("POSTGRES_TEST_DB_HOST", "postgres_test_db"),
                port=os.getenv("POSTGRES_TEST_DB_PORT", 5432),
                database="mydb",
                username="myuser",
                password="mypassword",
            ).save()
        if resource.dbtresource_set.count() == 0:
            DBTCoreDetails(
                resource=resource,
                project_path="fixtures/test_resources/jaffle_shop",
                threads=1,
                version=DBTVersion.V1_7.value,
                subtype=ResourceSubtype.DBT,
                database="mydb",
                schema="dbt_sl_test",
            ).save()

    return resource


def create_local_metabase(workspace):
    try:
        resource = Resource.objects.get(
            workspace=workspace, name="Test Metabase Resource", type=ResourceType.BI
        )
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, name="Test Metabase Resource", type=ResourceType.BI
        )
        if not hasattr(resource, "details") or not isinstance(
            resource.details, MetabaseDetails
        ):
            MetabaseDetails(
                resource=resource,
                username="test@example.com",
                password="mypassword1",
                connect_uri=os.getenv("TEST_METABASE_URI", "http://metabase:4000"),
            ).save()

    return resource
