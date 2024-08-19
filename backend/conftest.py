import os
import sys

import django
import pytest
from django.apps import apps

from app.models import (
    Asset,
    AssetLink,
    Column,
    ColumnLink,
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
from workflows.utils.debug import ContextDebugger

MOCK_WORKSPACE_ID = "mock_"


def pytest_addoption(parser):
    parser.addoption(
        "--internal", action="store_true", default=False, help="Run slow tests"
    )
    parser.addoption(
        "--recache", action="store_true", default=False, help="Recache fixtures"
    )


def pytest_configure(config):
    backend_path = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(backend_path, ".."))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    if project_root not in sys.path:
        sys.path.append(project_root)
    if not apps.ready:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
        django.setup()
    config.addinivalue_line("markers", "internal: mark test as internal")
    config.addinivalue_line(
        "markers", "nointernal: mark test to not run when --nointernal is provided"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--internal"):
        skip_nointernal = pytest.mark.skip(reason="skipped due to --runslow option")
        for item in items:
            if "nointernal" in item.keywords:
                item.add_marker(skip_nointernal)
    else:
        skip_internal = pytest.mark.skip(reason="need --internal option to run")
        for item in items:
            if "internal" in item.keywords:
                item.add_marker(skip_internal)


@pytest.fixture
def workspace():
    user = User.objects.create_user(
        name="Turntable Dev", email="dev@turntable.so", password="mypassword"
    )
    # create turntable full
    workspace = Workspace.objects.create(
        id="org_2XVt0EheumDcoCerhQzcUlVmXvG",
        name="Parkers Vinyl Shop",
    )
    workspace.add_admin(user)
    workspace.save()
    return workspace


@pytest.fixture()
def local_postgres(db, workspace):
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


@pytest.fixture()
def local_metabase(db, workspace):
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


def assert_ingest_output(resources):
    ## all tables have records
    assert Asset.objects.count() > 0
    assert AssetLink.objects.count() > 0
    assert Column.objects.count() > 0
    assert ColumnLink.objects.count() > 0

    ## all resources represented in assets
    for resource in resources:
        assert resource.asset_set.count() > 0

    ## at least one asset link across resources if multiple resources used
    if len(resources) > 1:
        links_across_resources = [
            v.id
            for v in AssetLink.objects.all()
            if v.source.resource.id != v.target.resource.id
        ]
        assert len(links_across_resources) > 0


@pytest.fixture()
def prepopulated_dev_db(local_metabase, local_postgres):
    resources = [local_metabase, local_postgres]
    # add in dev dbs
    for resource in resources:
        with open(
            f"fixtures/datahub_dbs/{resource.details.subtype}.duckdb", "rb"
        ) as f2:
            resource.datahub_db.save(
                f"{resource.details.subtype}.duckdb", f2, save=True
            )

        input = {
            "resource_id": resource.id,
        }
        context = ContextDebugger({"input": input})
        MetadataSyncWorkflow().process_metadata(context)

    # ensure output
    assert_ingest_output(resources)

    return resources


@pytest.fixture
def recache(request):
    return request.config.getoption("--recache")
