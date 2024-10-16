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
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfjTM6KSLm6fVYjLNYosPupbjDwavf6thtHje+pBg0QLgn9hR2W0kiHRoomMIc8OBVoYk8xzQOQDGlx4uoobdQwiONwEqAzdisKVsZSW1mejuBWpxxkzTQx3rVtAmy3bSspiGIqwFWbKAiWoHTvSq6XXriHrs4iZX1f9cnp6AE0FdG3xWYpYlC3wmeK010F/9U2RVYTMikUyPj8CPmNmH0E00f00Nlk43EjwITpcNt5nzzL8Mvet7c2Bh4udp2WVItnK0Jh4G1yYxKg7835vcRzVRwJiARbA9i7+9fzmHZHWEJucSw04M98pPdWyokBHpdRj8hBTXgjh5+wN92SVwL"
    private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA340zOiki5un1WIyzWKLD7qW4w8Gr3+rYbR43vqQYNEC4J/YU\ndltJIh0aKJjCHPDgVaGJPMc0DkAxpceLqKG3UMIjjcBKgM3YrClbGUltZno7gVqc\ncZM00Md61bQJst20rKYhiKsBVmygIlqB070qul164h67OImV9X/XJ6egBNBXRt8V\nmKWJQt8JnitNdBf/VNkVWEzIpFMj4/Aj5jZh9BNNH9NDZZONxI8CE6XDbeZ88y/D\nL3re3NgYeLnadllSLZytCYeBtcmMSoO/N+b3Ec1UcCYgEWwPYu/vX85h2R1hCbnE\nsNODPfKT3VsqJAR6XUY/IQU14I4efsDfdklcCwIDAQABAoIBADvf5LWSKP/x772M\nychWp+W2SztbFv69NsRbEJEmADmWj/xcA3UD1B2n78apy2vW9C7bOhemPwIGHYYK\nYRSEY8XkiYNA2nOPLpZF6Vlnej61RFTMARTGWaIFm5e7RdG7YdXQFTE2pAASzf0F\ngrpEczpBKVWA56In75s2Z1j+o3RGHIgBjnuVC1pK0JV+84jvaV5SWTHGWqqxGLnP\nQNtDKqGeNvmrrYq1u/f9K+tQRl5MJw14NlI+NluQaTgfcG8wE/BlGqCjALUiZLh4\nqEwNKs7Eh2b0qJjUJGvpiITdzJ1qzF7VaZWpWKqW7ws+vujn7hf+exAkgI1UBvY9\nS9W0JpkCgYEA/i/FX2AxyUuOJ/huly4fnI5dEKNQGNIj06xwga7JdsEXAUceMHvB\nzwL9eRwg0dKW6mQqc2z3gGvdb5CsKbC1C0UQ87tUMUf5XIknakQ3Uai8DiolpnUl\nUOgq2T9s7zRm/0atSFE/upUhhbfbAo/xXIn+8DG43KGZiHNJN5J+nn8CgYEA4SV6\nuFkKZKI2qRWmaXk4etfueCBKhG6IdjIpNhwBpusK/Rtka0ZLg9bUnCreP6sryrbR\nVfdUgB62P12ugSyKsbA/10P/K3/PFIr0kTRNhjrb85KkWhYiAJcBhJU56sWflu1r\nbJeJ5AzE9J8FWgfrwNJZ8kVd/FEL1FS03Y93FHUCgYEAj6wKwJ0Lpv6YzEjkoXkF\njyT8v3G/zTfB3lwif3p/DyuWyDcdfkQFSPAkuzbF6jNA8B1LzVAzGRhe4jeAyFPE\nESmpqkohDXXkIYS4jZ0fM33PRaZW/55JSFDiH0d1WENjUDjvqueZwOmYOA+yr+ES\niL7LJZLFLZf9wx1+rfWUshsCgYAXorefYrmUlvLmDT/LEs67FrASLFGmVXQ99EYf\nSBFkVIhyyc1g9aA31vW670UlqfKO9WJEhBJ64L6BKHSJWwO0Y6xQDPNcva4fmfbS\nx4rb7JHqoBpg2rH3HeMq5/+MhfKbBZGhdMclCbIjfA4zxWEafPq0VFPpiRiU0c+q\n8sStgQKBgQCNnh+y4QppC8UW8irxjZHNCuv+CUlHOjHhm82WHUm1flvDtIxHW3S8\nUKyhS4c9AgIywA7DXxSize7HpSZb3DqWg0DIq7FnRuHykLqPF0PiCMCi1sGWfp31\nMMLk7skCAIkXKyclGYQamgtuj87I13ZHnZYM4DwYgiklLXf8F5J4qw==\n-----END RSA PRIVATE KEY-----\n"
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
    git_repo_url = "git@github.com:turntable-so/jaffle-shop.git"
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
        if resource.dbtresource_set.count() == 0:
            DBTCoreDetails(
                resource=resource,
                project_path=(
                    "fixtures/test_resources/jaffle_shop" if repository is None else "."
                ),
                repository=repository,
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
