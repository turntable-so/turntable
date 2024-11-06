import json
import os

from app.models import (
    BigqueryDetails,
    DatabricksDetails,
    DBTCoreDetails,
    LookerDetails,
    PowerBIDetails,
    RedshiftDetails,
    Repository,
    Resource,
    ResourceType,
    SnowflakeDetails,
    TableauDetails,
    User,
    Workspace,
)
from fixtures.local_env import create_repository_n, create_ssh_key_n
from vinyl.lib.dbt_methods import DBTVersion


def create_user():
    email = os.getenv("STAGING_ADMIN_EMAIL")
    password = os.getenv("STAGING_ADMIN_PASSWORD")
    assert email, "must provide STAGING_ADMIN_EMAIL to use this test"
    assert password, "must provide STAGING_ADMIN_PASSWORD to use this test"
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return User.objects.create_user(
            name="Turntable Staging admin", email=email, password=password
        )


def create_workspace_n(user, dialect, n, workspace_id=None):
    if not workspace_id:
        workspace_id = os.getenv(f"{dialect.upper()}_{n}_WORKSPACE_ID")
    workspace_name = os.getenv(f"{dialect.upper()}_{n}_WORKSPACE_NAME")
    assert (
        workspace_id
    ), f"must provide {dialect.upper()}_{n}_WORKSPACE_ID to use this test"
    assert (
        workspace_name
    ), f"must provide {dialect.upper()}_{n}_WORKSPACE_NAME to use this test"
    try:
        return Workspace.objects.get(id=workspace_id)
    except Workspace.DoesNotExist:
        workspace = Workspace.objects.create(
            id=workspace_id,
            name=workspace_name,
        )
        workspace.add_admin(user)
        workspace.save()
        user_info = json.loads(os.getenv(f"{dialect.upper()}_{n}_USER_INFO", "[]"))
        for info in user_info:
            try:
                user = User.objects.get(email=info["email"])
            except User.DoesNotExist:
                user = User.objects.create_user(
                    name=info["name"],
                    email=info["email"],
                )
                if info.get("admin"):
                    workspace.add_admin(user)
                else:
                    workspace.add_member(user)
        return workspace


def create_bigquery_n(workspace, n):
    gac = os.getenv(f"BIGQUERY_{n}_GOOGLE_APPLICATION_CREDENTIALS")
    resource_name = os.getenv(f"BIGQUERY_{n}_RESOURCE_NAME")
    schema_include = os.getenv(f"BIGQUERY_{n}_SCHEMA_INCLUDE")
    if schema_include:
        schema_include = json.loads(schema_include)

    assert (
        gac
    ), f"must provide BIGQUERY_{n}_GOOGLE_APPLICATION_CREDENTIALS to use this test"
    assert resource_name, f"must provide BIGQUERY_{n}_RESOURCE_NAME to use this test"
    # assert schema_include, f"must provide BIGQUERY_{n}_SCHEMA_INCLUDE to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.DB, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, BigqueryDetails
    ):
        BigqueryDetails(
            name=resource_name,
            workspace=workspace,
            resource=resource,
            lookback_days=1,
            schema_include=schema_include,
            service_account=json.loads(gac.replace("\n", "\\n")),
        ).save()
    return resource


def create_snowflake_n(workspace, n):
    username = os.getenv(f"SNOWFLAKE_{n}_USER")
    password = os.getenv(f"SNOWFLAKE_{n}_PASSWORD")
    account = os.getenv(f"SNOWFLAKE_{n}_ACCOUNT")
    warehouse = os.getenv(f"SNOWFLAKE_{n}_WAREHOUSE")
    role = os.getenv(f"SNOWFLAKE_{n}_ROLE")
    resource_name = os.getenv(f"SNOWFLAKE_{n}_RESOURCE_NAME")

    assert username, f"must provide SNOWFLAKE_{n}_USER to use this test"
    assert password, f"must provide SNOWFLAKE_{n}_PASSWORD to use this test"
    assert account, f"must provide SNOWFLAKE_{n}_ACCOUNT to use this test"
    assert warehouse, f"must provide SNOWFLAKE_{n}_WAREHOUSE to use this test"
    assert role, f"must provide SNOWFLAKE_{n}_ROLE to use this test"
    assert resource_name, f"must provide SNOWFLAKE_{n}_RESOURCE_NAME to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.DB, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, SnowflakeDetails
    ):
        SnowflakeDetails(
            resource=resource,
            workspace=workspace,
            username=username,
            password=password,
            account=account,
            warehouse=warehouse,
            role=role,
        ).save()
    return resource


def create_databricks_n(workspace, n):
    host = os.getenv(f"DATABRICKS_{n}_HOST")
    token = os.getenv(f"DATABRICKS_{n}_TOKEN")
    http_path = os.getenv(f"DATABRICKS_{n}_HTTP_PATH")
    resource_name = os.getenv(f"DATABRICKS_{n}_RESOURCE_NAME")

    assert host, f"must provide DATABRICKS_{n}_HOST to use this test"
    assert token, f"must provide DATABRICKS_{n}_TOKEN to use this test"
    assert http_path, f"must provide DATABRICKS_{n}_HTTP_PATH to use this test"
    assert resource_name, f"must provide DATABRICKS_{n}_RESOURCE_NAME to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.DB, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, DatabricksDetails
    ):
        DatabricksDetails(
            resource=resource,
            workspace=workspace,
            host=host,
            token=token,
            http_path=http_path,
        ).save()

    return resource


def create_redshift_n(workspace: Workspace, n):
    host = os.getenv(f"REDSHIFT_{n}_HOST")
    port = os.getenv(f"REDSHIFT_{n}_PORT")
    database = os.getenv(f"REDSHIFT_{n}_DATABASE")
    username = os.getenv(f"REDSHIFT_{n}_USER")
    password = os.getenv(f"REDSHIFT_{n}_PASSWORD")
    serverless = os.getenv(f"REDSHIFT_{n}_SERVERLESS", "false") == "true"
    resource_name = os.getenv(f"REDSHIFT_{n}_RESOURCE_NAME")

    assert host, f"must provide REDSHIFT_{n}_HOST to use this test"
    assert port, f"must provide REDSHIFT_{n}_PORT to use this test"
    assert database, f"must provide REDSHIFT_{n}_DATABASE to use this test"
    assert username, f"must provide REDSHIFT_{n}_USER to use this test"
    assert password, f"must provide REDSHIFT_{n}_PASSWORD to use this test"
    assert serverless, f"must provide REDSHIFT_{n}_SERVERLESS to use this test"
    assert resource_name, f"must provide REDSHIFT_{n}_RESOURCE_NAME to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.DB, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, RedshiftDetails
    ):
        RedshiftDetails(
            resource=resource,
            workspace=workspace,
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            serverless=serverless,
        ).save()

    return resource


def create_dbt_n(
    resource: Resource, n, force_db: bool = False, repository: Repository | None = None
):
    database = os.getenv(f"DBT_{n}_DATABASE")
    schema = os.getenv(f"DBT_{n}_SCHEMA")
    dbt_version = os.getenv(f"DBT_{n}_VERSION")
    assert database, f"must provide DBT_{n}_DATABASE to use this test"
    assert schema, f"must provide DBT_{n}_SCHEMA to use this test"
    assert dbt_version, f"must provide DBT_{n}_VERSION to use this test"

    project_path = os.getenv(f"DBT_{n}_PROJECT_PATH", ".")

    if force_db:
        if isinstance(resource.details, BigqueryDetails):
            database = resource.details.service_account_dict.get("project_id", database)
        else:
            raise ValueError("force_db is only supported for BigQuery resources")

    dbt_major, dbt_minor = dbt_version.split(".")
    other_schemas = os.getenv(f"DBT_{n}_OTHER_SCHEMAS")
    if other_schemas:
        other_schemas = json.loads(other_schemas)

    DBTCoreDetails(
        resource=resource,
        workspace=workspace,
        repository=repository,
        project_path=project_path,
        threads=os.getenv(f"DBT_{n}_THREADS", 6),
        other_schemas=other_schemas,
        database=database,
        version=getattr(DBTVersion, f"V{dbt_major}_{dbt_minor}").value,
        schema=schema,
    ).save()
    return resource


def create_looker_n(workspace, n, git_repo: Repository | None = None):
    looker_secret = os.getenv(f"LOOKER_{n}_SECRET")
    looker_url = os.getenv(f"LOOKER_{n}_URL")
    resource_name = os.getenv(f"LOOKER_{n}_RESOURCE_NAME")

    assert looker_secret, f"must provide LOOKER_{n}_SECRET to use this test"
    assert looker_url, f"must provide LOOKER_{n}_URL to use this test"
    assert resource_name, f"must provide LOOKER_{n}_RESOURCE_NAME to use this test"
    assert git_repo or os.getenv(f"LOOKER_{n}_project_path")

    looker_secret_json = json.loads(looker_secret)

    looker, _ = Resource.objects.get_or_create(
        name=resource_name, type=ResourceType.BI, workspace=workspace
    )
    if not hasattr(looker, "details") or not isinstance(looker.details, LookerDetails):
        LookerDetails(
            resource=looker,
            workspace=workspace,
            base_url=looker_url,
            client_id=looker_secret_json["client_id"],
            client_secret=looker_secret_json["client_secret"],
            repository=git_repo,
            project_path=os.getenv(f"LOOKER_{n}_PROJECT_PATH", "."),
        ).save()

    return looker


def create_tableau_n(workspace, n):
    connect_uri = os.getenv(f"TABLEAU_{n}_CONNECT_URI")
    username = os.getenv(f"TABLEAU_{n}_USERNAME")
    password = os.getenv(f"TABLEAU_{n}_PASSWORD")
    resource_name = os.getenv(f"TABLEAU_{n}_RESOURCE_NAME")

    assert connect_uri, f"must provide TABLEAU_{n}_CONNECT_URI to use this test"
    assert username, f"must provide TABLEAU_{n}_USERNAME to use this test"
    assert password, f"must provide TABLEAU_{n}_PASSWORD to use this test"
    assert resource_name, f"must provide TABLEAU_{n}_RESOURCE_NAME to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.BI, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, TableauDetails
    ):
        TableauDetails(
            resource=resource,
            workspace=workspace,
            connect_uri=connect_uri,
            site=os.getenv(f"TABLEAU_{n}_SITE", ""),
            username=username,
            password=password,
        ).save()

    return resource


def create_powerbi_n(workspace, n):
    resource_name = os.getenv(f"POWERBI_{n}_RESOURCE_NAME")
    client_id = os.getenv(f"POWERBI_{n}_CLIENT_ID")
    client_secret = os.getenv(f"POWERBI_{n}_CLIENT_SECRET")
    tenant_id = os.getenv(f"POWERBI_{n}_TENANT_ID")
    workspace_id = os.getenv(f"POWERBI_{n}_WORKSPACE_ID")

    assert resource_name, f"must provide POWERBI_{n}_RESOURCE_NAME to use this test"
    assert client_id, f"must provide POWERBI_{n}_CLIENT_ID to use this test"
    assert client_secret, f"must provide POWERBI_{n}_CLIENT_SECRET to use this test"
    assert tenant_id, f"must provide POWERBI_{n}_TENANT_ID to use this test"

    resource, _ = Resource.objects.get_or_create(
        workspace=workspace, type=ResourceType.BI, name=resource_name
    )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, PowerBIDetails
    ):
        PowerBIDetails(
            resource=resource,
            workspace=workspace,
            client_id=client_id,
            client_secret=client_secret,
            powerbi_tenant_id=tenant_id,
            powerbi_workspace_id=workspace_id,
        ).save()

    return resource


### GROUPS
def group_1(user):
    workspace = create_workspace_n(user, "bigquery", 1)
    bigquery = create_bigquery_n(workspace, 1)
    sshkey1 = create_ssh_key_n(workspace, 1)
    repository1 = create_repository_n(workspace, 1, sshkey1)
    sshkey2 = create_ssh_key_n(workspace, 2)
    repository2 = create_repository_n(workspace, 2, sshkey2)
    create_dbt_n(bigquery, 1, force_db=True, repository=repository1)
    create_dbt_n(bigquery, 2, force_db=True, repository=repository2)
    return [bigquery]


def group_2(user):
    workspace = create_workspace_n(user, "snowflake", 0)
    snowflake = create_snowflake_n(workspace, 0)
    sshkey = create_ssh_key_n(workspace, 0)
    repository = create_repository_n(workspace, 0, sshkey)
    create_dbt_n(snowflake, 0, repository=repository)

    return [snowflake]


def group_3(user):
    workspace = create_workspace_n(user, "databricks", 0)
    databricks = create_databricks_n(workspace, 0)
    tableau = create_tableau_n(workspace, 0)
    sshkey = create_ssh_key_n(workspace, 0)
    repository = create_repository_n(workspace, 0, sshkey)
    create_dbt_n(databricks, 0, repository=repository)

    return [databricks, tableau]


def group_4(user):
    workspace = create_workspace_n(user, "bigquery", 0)
    bigquery = create_bigquery_n(workspace, 0)
    sshkey = create_ssh_key_n(workspace, 0)
    repository = create_repository_n(workspace, 0, sshkey)
    create_dbt_n(
        bigquery, 0, force_db=True, repository=repository
    )  # force_db=True to use the same project_id as the bigquery resource. Can't use mydb because it is reserved.

    powerbi = create_powerbi_n(workspace, 0)
    return [bigquery, powerbi]


def group_5(user):
    workspace = create_workspace_n(user, "redshift", 0)
    redshift = create_redshift_n(workspace, 0)
    sshkey = create_ssh_key_n(workspace, 0)
    repository = create_repository_n(workspace, 0, sshkey)
    create_dbt_n(redshift, 0, repository=repository)

    return [redshift]


def group_6(user):
    workspace = create_workspace_n(user, "bigquery", 3)
    bigquery = create_bigquery_n(workspace, 3)
    sshkey = create_ssh_key_n(workspace, 3)
    repository = create_repository_n(workspace, 3, sshkey)
    create_dbt_n(bigquery, 5, force_db=True, repository=repository)
    return [bigquery]
