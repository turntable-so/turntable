import os
import shutil
from unittest.mock import create_autospec

import pytest
from django.conf import settings

from app.models import Workspace
from app.models.project import Project
from app.models.ssh_key import SSHKey
from app.models.workspace import generate_short_uuid
from app.utils.test_utils import require_env_vars

TEST_WORKSPACE_ID = generate_short_uuid()


isolate_mark = pytest.mark.parametrize(
    "isolate", [True, False] if not os.getenv("GITHUB_RUN_ID") else [True]
)


@require_env_vars("SSHKEY_0_PUBLIC", "SSHKEY_0_PRIVATE")
class TestRepository:
    @pytest.fixture(scope="session", autouse=True)
    def run_command_after_tests(request):
        yield
        # This will run after all tests are completed
        path_to_delete = os.path.join(settings.MEDIA_ROOT, "ws", TEST_WORKSPACE_ID)
        if os.path.exists(path_to_delete):
            shutil.rmtree(path_to_delete)

    @pytest.fixture
    def local_postgres_repo(self, local_postgres):
        repo = local_postgres.dbtresource_set.first().repository
        return repo

    @pytest.fixture
    def local_postgres_test_project(self, local_postgres_repo):
        return Project.objects.create(
            workspace=local_postgres_repo.workspace,
            repository=local_postgres_repo,
            branch_name="test-branch",
            schema="test_schema",
        )

    def test_repo_connection(self, local_postgres_repo):
        res = local_postgres_repo.test_remote_repo_connection()
        assert res["success"]

    def test_clone(self, local_postgres_repo):
        assert local_postgres_repo.main_project.clone()

    @isolate_mark
    def test_repo_context(self, local_postgres_repo, isolate):
        with local_postgres_repo.main_project.repo_context(isolate=isolate) as (
            repo,
            _,
        ):
            assert len(os.listdir(repo.working_tree_dir)) > 3

    @isolate_mark
    def test_dbt_repo_context_with_schema(
        self,
        local_postgres,
        local_postgres_test_project,
        isolate,
    ):
        # Create a spy on the real method
        spy = create_autospec(
            local_postgres.details.get_dbt_profile_contents, wraps=True
        )
        local_postgres.details.get_dbt_profile_contents = spy

        with local_postgres.dbtresource_set.first().dbt_repo_context(
            isolate=isolate, project_id=local_postgres_test_project.id
        ) as (project, filepath, _):
            assert project != None
            assert filepath != None
            profiles_yml_path = os.path.join(project.dbt_profiles_dir, "profiles.yml")
            with open(profiles_yml_path, "r") as f:
                assert "schema: test_schema" in f.read()

    @isolate_mark
    def test_checkout(self, local_postgres_test_project, isolate):
        with local_postgres_test_project.repo_context(isolate=isolate) as (
            repo,
            env,
        ):
            assert (
                local_postgres_test_project.checkout(isolate, repo, env)
                == local_postgres_test_project.branch_name
            )

    def test_create_branch(self, local_postgres_repo):
        branch_name = "test_branch" + "".join([hex(x)[2:] for x in os.urandom(32)])
        project = Project.objects.create(
            workspace=local_postgres_repo.workspace,
            repository=local_postgres_repo,
            branch_name=branch_name,
        )
        assert (
            project.create_git_branch(
                source_branch=local_postgres_repo.main_project.branch_name
            )
            == branch_name
        )
        project.clone()
        assert project.checkout() == branch_name

    def test_pull(self, local_postgres_test_project):
        assert local_postgres_test_project.git_pull()

    def test_generate_deploy_key(self):
        workspace = Workspace.objects.create(
            id=TEST_WORKSPACE_ID + "1",
            name="Test workspace 1",
        )
        key = SSHKey.generate_deploy_key(workspace)
        assert key.public_key is not None
