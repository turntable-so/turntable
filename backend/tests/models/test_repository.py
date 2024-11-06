import os
import shutil
import tempfile
from unittest.mock import patch

from fixtures.local_env import (
    create_local_postgres,
    create_local_user,
    create_local_workspace,
    create_repository_n,
    create_ssh_key_n,
)
import pytest
from django.conf import settings

from app.models import Workspace
from app.models.repository import Branch
from app.models.ssh_key import SSHKey
from app.models.workspace import generate_short_uuid
from app.utils.test_utils import require_env_vars

TEST_WORKSPACE_ID = generate_short_uuid()


isolate_mark = pytest.mark.parametrize(
    "isolate", [True, False] if not os.getenv("GITHUB_RUN_ID") else [True]
)


@pytest.fixture(autouse=True, scope="session")
def setup_temp_media_root(tmp_path_factory):
    # Create a temporary directory for all tests in the class
    temp_media = tmp_path_factory.mktemp("media")

    # Patch the MEDIA_ROOT setting for all tests in this class
    with patch.object(settings, "MEDIA_ROOT", str(temp_media)):
        yield temp_media


@pytest.fixture(scope="function")
def initialized_repo():
    user = create_local_user()
    workspace = create_local_workspace(user)
    ssh_key = create_ssh_key_n(workspace, 0)
    git_repo = create_repository_n(workspace, 0, ssh_key)
    # Clone the repo once for all tests in the class
    postgres = create_local_postgres(workspace, git_repo)

    postgres.repository.main_branch.clone()
    breakpoint()
    return postgres.repository


@pytest.mark.django_db
def test_repo_connection(
    initialized_repo,
):
    breakpoint()
    res = initialized_repo.test_repo_connection()
    assert res["success"]


@isolate_mark
def test_repo_context(initialized_repo, isolate):
    with initialized_repo.main_branch.repo_context(isolate=isolate) as (repo, _):
        assert len(os.listdir(repo.working_tree_dir)) > 3


@pytest.mark.django_db
def test_dbt_repo_context(local_postgres, isolate):
    with local_postgres.dbtresource_set.first().dbt_repo_context(isolate=isolate) as (
        project,
        filepath,
        _,
    ):
        assert project != None
        assert filepath != None


@isolate_mark
def test_clone_repo_if_not_exists(self, initialized_repo, isolate):
    with initialized_repo.main_branch.repo_context(isolate=isolate) as (repo, _):
        assert repo.active_branch.name == initialized_repo.main_branch_name


@isolate_mark
def test_get_repo_if_already_exists(self, initialized_repo, isolate):
    with initialized_repo.main_branch.repo_context(isolate=isolate) as (repo, _):
        assert repo is not None

        with initialized_repo.main_branch.repo_context(
            isolate=isolate, repo_override=repo
        ) as (repo2, _):
            assert repo2 is not None


@isolate_mark
def test_get_working_tree(self, initialized_repo, isolate):
    with initialized_repo.main_branch.repo_context(isolate=isolate) as (repo, _):
        assert repo.working_tree_dir is not None


@isolate_mark
def test_switch_branch(self, local_postgres_test_branch, isolate):
    with local_postgres_test_branch.repo_context(isolate=isolate) as (
        repo,
        env,
    ):
        assert (
            local_postgres_test_branch.switch_to_git_branch(isolate, repo, env)
            == local_postgres_test_branch.branch_name
        )


@isolate_mark
def test_create_branch(self, initialized_repo, isolate):
    branch_name = "test_branch" + "".join([hex(x)[2:] for x in os.urandom(32)])
    branch = Branch.objects.create(
        workspace=initialized_repo.workspace,
        repository=initialized_repo,
        branch_name=branch_name,
    )
    try:
        assert branch.create_git_branch(isolate=isolate) == branch_name
    finally:
        branch.delete_files()


@isolate_mark
def test_pull(self, local_postgres_test_branch, isolate):
    assert local_postgres_test_branch.git_pull(isolate=isolate)


@isolate_mark
def test_commit_and_push(self, local_postgres_test_branch, isolate):
    with local_postgres_test_branch.repo_context(isolate=isolate) as (repo, env):
        assert (
            local_postgres_test_branch.switch_to_git_branch(isolate, repo, env)
            == local_postgres_test_branch.branch_name
        )
        path = os.path.join(repo.working_tree_dir, "README.md")
        with open(path, "a") as f:
            f.write("\n" + "".join([hex(x)[2:] for x in os.urandom(32)]))
        assert repo.is_dirty(untracked_files=True)

        assert local_postgres_test_branch.git_commit_and_push(
            "Add random hex string to README.md", isolate, repo, env
        )

        assert not repo.is_dirty(untracked_files=True)


def test_generate_deploy_key(self):
    workspace = Workspace.objects.create(
        id=TEST_WORKSPACE_ID + "1",
        name="Test workspace 1",
    )
    key = SSHKey.generate_deploy_key(workspace)
    assert key.public_key is not None
