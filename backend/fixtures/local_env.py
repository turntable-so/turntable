import os

from app.models import (
    DBTCoreDetails,
    MetabaseDetails,
    PostgresDetails,
    Repository,
    Resource,
    ResourceSubtype,
    ResourceType,
    SSHKey,
    User,
    Workspace,
)
from app.models.resources import EnvironmentType
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
        return Workspace.objects.get(id=0)
    except Workspace.DoesNotExist:
        workspace = Workspace.objects.create(
            id=0,
            name="Parkers Vinyl Shop",
        )
        workspace.add_admin(user)
        workspace.save()
        return workspace


def create_ssh_key_n(workspace, n):
    public_key = os.getenv(f"SSHKEY_{n}_PUBLIC")
    private_key = os.getenv(f"SSHKEY_{n}_PRIVATE")
    assert public_key, f"must provide SSHKEY_{n}_PUBLIC to use this test"
    assert private_key, f"must provide SSHKEY_{n}_PRIVATE to use this test"
    private_key = private_key.replace("\\n", "\n")
    cur_keys = SSHKey.objects.filter(workspace=workspace)
    for key in cur_keys:
        if key.public_key == public_key and key.private_key == private_key:
            return key

    return SSHKey.objects.create(
        workspace=workspace,
        public_key=public_key,
        private_key=private_key,
    )


def create_repository_n(workspace, n, ssh_key):
    assert ssh_key, "must provide ssh_key to use this test"
    git_repo_url = os.getenv(f"GIT_{n}_REPO_URL")
    assert git_repo_url, f"must provide GIT_{n}_REPO_URL to use this test"
    return Repository.objects.get_or_create(
        workspace=workspace, git_repo_url=git_repo_url, ssh_key=ssh_key
    )[0]


def create_local_postgres(workspace, repository: Repository | None = None):
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
        environment_map = {
            "dev": EnvironmentType.DEV,
            "dbt_sl_test": EnvironmentType.PROD,
        }
        for schema, env_type in environment_map.items():
            if resource.dbtresource_set.filter(environment=env_type).count() == 0:
                DBTCoreDetails(
                    resource=resource,
                    workspace=workspace,
                    project_path=(
                        "fixtures/test_resources/jaffle_shop"
                        if repository is None
                        else "."
                    ),
                    repository=repository,
                    threads=1,
                    version=DBTVersion.V1_7.value,
                    subtype=ResourceSubtype.DBT,
                    database="mydb",
                    schema=schema,
                    environment=env_type,
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
                workspace=workspace,
                username="test@example.com",
                password="mypassword1",
                connect_uri=os.getenv("TEST_METABASE_URI", "http://metabase:4000"),
            ).save()

    return resource
