import json
import os

from app.models import (
    BigqueryDetails,
    DatabricksDetails,
    DBTCoreDetails,
    GithubInstallation,
    LookerDetails,
    Resource,
    ResourceType,
    SnowflakeDetails,
    TableauDetails,
    User,
    Workspace,
)
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


def create_workspace_n(user, dialect, n):
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

    try:
        resource = Resource.objects.get(workspace=workspace, type=ResourceType.DB)
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, type=ResourceType.DB, name=resource_name
        )
    if not hasattr(resource, "details") or not isinstance(
        resource.details, BigqueryDetails
    ):
        BigqueryDetails(
            name=resource_name,
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
    try:
        resource = Resource.objects.get(workspace=workspace, type=ResourceType.DB)
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, type=ResourceType.DB, name=resource_name
        )
    if not hasattr(resource, "details") or not isinstance(
        resource.details, SnowflakeDetails
    ):
        SnowflakeDetails(
            resource=resource,
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

    try:
        resource = Resource.objects.get(workspace=workspace, type=ResourceType.DB)
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, type=ResourceType.DB, name=resource_name
        )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, DatabricksDetails
    ):
        DatabricksDetails(
            resource=resource,
            host=host,
            token=token,
            http_path=http_path,
        ).save()

    return resource


def create_dbt_n(resource: Resource, n):
    database = os.getenv(f"DBT_{n}_DATABASE")
    schema = os.getenv(f"DBT_{n}_SCHEMA")
    dbt_version = os.getenv(f"DBT_{n}_VERSION")
    assert database, f"must provide DBT_{n}_DATABASE to use this test"
    assert schema, f"must provide DBT_{n}_SCHEMA to use this test"
    assert dbt_version, f"must provide DBT_{n}_VERSION to use this test"

    github_installation_id = os.getenv(f"DBT_{n}_GITHUB_INSTALLATION_ID")
    github_repo_id = os.getenv(f"DBT_{n}_GITHUB_REPO_ID")
    project_path = os.getenv(f"DBT_{n}_PROJECT_PATH", ".")

    if github_installation_id:
        try:
            github_installation = GithubInstallation.objects.get(
                id=github_installation_id
            )
        except GithubInstallation.DoesNotExist:
            github_installation = GithubInstallation.objects.create(
                id=github_installation_id, workspace=resource.workspace
            )

    dbt_major, dbt_minor = dbt_version.split(".")
    other_schemas = os.getenv(f"DBT_{n}_OTHER_SCHEMAS")
    if other_schemas:
        other_schemas = json.loads(other_schemas)

    for dbtres in resource.dbtresource_set.all():
        dbt_resource_already_created = (
            (
                not github_installation_id
                or dbtres.github_installation == github_installation
            )
            and (not github_repo_id or dbtres.github_repo_id == github_repo_id)
            and (project_path == dbtres.project_path)
        )
        if dbt_resource_already_created:
            return resource

    DBTCoreDetails(
        resource=resource,
        github_installation_id=github_installation_id,
        github_repo_id=github_repo_id,
        project_path=os.getenv(f"DBT_{n}_PROJECT_PATH", "."),
        threads=os.getenv(f"DBT_{n}_THREADS", 6),
        other_schemas=other_schemas,
        database=database,
        version=getattr(DBTVersion, f"V{dbt_major}_{dbt_minor}").value,
        schema=schema,
    ).save()
    return resource


def create_looker_n(workspace, n):
    looker_secret = os.getenv(f"LOOKER_{n}_SECRET")
    looker_url = os.getenv(f"LOOKER_{n}_URL")
    github_installation_id = os.getenv(f"LOOKER_{n}_GITHUB_INSTALLATION_ID")
    github_repo_id = os.getenv(f"LOOKER_{n}_GITHUB_REPO_ID")
    resource_name = os.getenv(f"LOOKER_{n}_RESOURCE_NAME")

    assert looker_secret, f"must provide LOOKER_{n}_SECRET to use this test"
    assert (
        github_installation_id
    ), f"must provide LOOKER_{n}_GITHUB_INSTALLATION_ID to use this test"
    assert github_repo_id, f"must provide LOOKER_{n}_GITHUB_REPO_ID to use this test"
    assert resource_name, f"must provide LOOKER_{n}_RESOURCE_NAME to use this test"

    looker_secret_json = json.loads(looker_secret)

    github_installation, _ = GithubInstallation.objects.update_or_create(
        id=github_installation_id, workspace=workspace
    )

    looker, _ = Resource.objects.update_or_create(
        name=resource_name, type=ResourceType.BI, workspace=workspace
    )
    if not hasattr(looker, "details") or not isinstance(looker.details, LookerDetails):
        LookerDetails(
            resource=looker,
            base_url=looker_url,
            client_id=looker_secret_json["client_id"],
            client_secret=looker_secret_json["client_secret"],
            github_installation=github_installation,
            github_repo_id=github_repo_id,
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

    try:
        resource = Resource.objects.get(workspace=workspace, type=ResourceType.BI)
    except Resource.DoesNotExist:
        resource = Resource.objects.create(
            workspace=workspace, type=ResourceType.BI, name=resource_name
        )

    if not hasattr(resource, "details") or not isinstance(
        resource.details, TableauDetails
    ):
        TableauDetails(
            resource=resource,
            connect_uri=connect_uri,
            site=os.getenv(f"TABLEAU_{n}_SITE", ""),
            username=username,
            password=password,
        ).save()

    return resource


### GROUPS
def group_1(user):
    workspace = create_workspace_n(user, "bigquery", 1)
    bigquery = create_bigquery_n(workspace, 1)
    create_dbt_n(bigquery, 1)
    create_dbt_n(bigquery, 2)
    return [bigquery]


def group_2(user):
    workspace = create_workspace_n(user, "snowflake", 1)
    snowflake = create_snowflake_n(workspace, 1)
    create_dbt_n(snowflake, 1)

    return [snowflake]


def group_3(user):
    workspace = create_workspace_n(user, "bigquery", 2)
    bigquery = create_bigquery_n(workspace, 2)
    create_dbt_n(bigquery, 4)
    looker = create_looker_n(workspace, 1)

    return [bigquery, looker]


def group_4(user):
    workspace = create_workspace_n(user, "databricks", 1)
    databricks = create_databricks_n(workspace, 1)
    tableau = create_tableau_n(workspace, 1)
    create_dbt_n(databricks, 5)

    return [databricks, tableau]
