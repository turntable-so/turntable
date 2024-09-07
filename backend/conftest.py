import os
import sys

import django
import pytest
from django.apps import apps

from app.utils.test_utils import assert_ingest_output
from fixtures.local_env import (
    create_local_metabase,
    create_local_postgres,
    create_local_user,
    create_local_workspace,
)
from fixtures.staging_env import group_2, group_4, group_5
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


@pytest.fixture()
def user():
    return create_local_user()


@pytest.fixture
def local_postgres(user):
    workspace = create_local_workspace(user)
    return create_local_postgres(workspace)


@pytest.fixture
def local_metabase(user):
    workspace = create_local_workspace(user)
    return create_local_metabase(workspace)


@pytest.fixture
def remote_snowflake(user):
    return group_2(user)[0]


@pytest.fixture
def remote_databricks(user):
    return group_4(user)[0]


@pytest.fixture
def remote_tableau(user):
    return group_4(user)[1]


@pytest.fixture
def remote_bigquery(user):
    return group_5(user)[0]


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
