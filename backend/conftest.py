import logging
import os
import sys

import django
import pytest
from celery import Celery
from celery.contrib.testing.worker import start_worker
from django.apps import apps
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from app.utils.test_utils import assert_ingest_output
from app.workflows.metadata import process_metadata
from app.workflows.tests.utils import TEST_QUEUE
from fixtures.local_env import (
    create_local_metabase,
    create_local_postgres,
    create_local_user,
    create_local_workspace,
    create_repository_n,
    create_ssh_key_n,
)
from fixtures.staging_env import group_1, group_2, group_3, group_4, group_5, group_6

MOCK_WORKSPACE_ID = "mock_"

pytest_plugins = ["celery.contrib.pytest"]


def pytest_addoption(parser):
    parser.addoption(
        "--internal", action="store_true", default=False, help="Run slow tests"
    )
    parser.addoption(
        "--recache", action="store_true", default=False, help="Recache fixtures"
    )
    parser.addoption(
        "--use_cache", action="store_true", default=False, help="Use cached fixtures"
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
def workspace(user):
    return create_local_workspace(user)


@pytest.fixture
def client(user, workspace):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def client_with_token(user, workspace):
    client = APIClient()
    token = str(AccessToken.for_user(user))
    client.force_authenticate(user=user, token=token)
    client.access_token = token
    return client


@pytest.fixture
def local_postgres(workspace):
    git_repo = None
    if os.getenv("SSHKEY_0_PUBLIC") and os.getenv("SSHKEY_0_PRIVATE"):
        ssh_key = create_ssh_key_n(workspace, 0)
        git_repo = create_repository_n(workspace, 0, ssh_key)
    return create_local_postgres(workspace, git_repo)


@pytest.fixture
def local_metabase(workspace):
    return create_local_metabase(workspace)


@pytest.fixture
def remote_snowflake(user):
    return group_2(user)[0]


@pytest.fixture
def remote_databricks(user):
    return group_3(user)[0]


@pytest.fixture
def remote_tableau(user):
    return group_3(user)[1]


@pytest.fixture
def remote_bigquery(user):
    return group_4(user)[0]


@pytest.fixture
def remote_powerbi(user):
    return group_4(user)[1]


@pytest.fixture
def remote_redshift(user):
    return group_5(user)[0]


@pytest.fixture
def internal_bigquery(user):
    return group_6(user)[0]


@pytest.fixture
def internal_bigquery_deprecated(user):
    return group_1(user)[0]


@pytest.fixture
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

        process_metadata(resource_id=resource.id, workspace_id=resource.workspace.id)

    # ensure output
    assert_ingest_output(resources)

    return resources


@pytest.fixture
def recache(request):
    return request.config.getoption("--recache")


@pytest.fixture
def use_cache(request):
    return request.config.getoption("--use_cache")


@pytest.fixture
def force_isolate(monkeypatch):
    monkeypatch.setenv("FORCE_ISOLATE", "true")


@pytest.fixture
def enable_django_allow_async_unsafe(monkeypatch):
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture(autouse=True)
def vinyl_read_only(monkeypatch):
    monkeypatch.setenv("VINYL_READ_ONLY", "true")


@pytest.fixture(scope="session")
def session_monkeypatch():
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="session")
def bypass_celery_beat(session_monkeypatch):
    session_monkeypatch.setenv("BYPASS_CELERY_BEAT", "true")


@pytest.fixture(scope="session")
def test_queue_name():
    """Generate unique queue name for each pytest-xdist worker"""
    worker_id = os.getenv("PYTEST_XDIST_WORKER")
    if not worker_id or worker_id == "master":
        return TEST_QUEUE
    return f"{TEST_QUEUE}_{worker_id}"


@pytest.fixture(scope="session")
def custom_celery_app(test_queue_name):
    app = Celery("api")

    # Load configuration from Django settings
    app.config_from_object("django.conf:settings", namespace="CELERY")

    app.conf.update(task_default_queue=test_queue_name, task_always_eager=False)

    app.autodiscover_tasks()

    return app


@pytest.fixture(scope="session")
def custom_celery_worker(
    custom_celery_app,
    test_queue_name,
    max_retries: int = 10,
):
    retry_count = 0

    while retry_count < max_retries:
        try:
            with start_worker(
                custom_celery_app,
                loglevel="info",
                queues=[test_queue_name],
                perform_ping_check=False,
                concurrency=1,
            ) as worker:
                yield worker
                break  # If we get here successfully, exit the retry loop
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                raise Exception(
                    f"Failed to start Celery worker after {max_retries} attempts: {str(e)}"
                )
            logging.warning(
                f"Celery worker failed, attempt {retry_count} of {max_retries}. Error: {str(e)}"
            )


@pytest.fixture(scope="session")
def suppress_celery_errors():
    """
    Suppress error logs from celery.worker.control and kombu.pidbox
    by setting their log levels to CRITICAL.
    """
    loggers_to_suppress = [
        "celery.worker.control",
        "kombu.pidbox",
        # You can add more loggers here if needed
    ]

    # Store original levels and update loggers
    original_levels = {}
    for logger_name in loggers_to_suppress:
        logger = logging.getLogger(logger_name)
        original_levels[logger_name] = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)

    yield

    # Restore original levels
    for logger_name, original_level in original_levels.items():
        logging.getLogger(logger_name).setLevel(original_level)


@pytest.fixture(scope="session")
def custom_celery(custom_celery_worker, bypass_celery_beat, suppress_celery_errors):
    return custom_celery_worker
