import json
import os
import shutil

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from app.models import User, Workspace
from app.models.git_connections import Branch, Repository, SSHKey
from app.models.resources import BigqueryDetails, DBTCoreDetails, Resource, ResourceType
from app.models.workspace import generate_short_uuid
from vinyl.lib.dbt_methods import DBTVersion

TEST_WORKSPACE_ID = generate_short_uuid()


class GitConnectionHelper:
    git_repo_url = "git@github.com:turntable-so/jaffle-shop.git"
    # test keys, not used in production
    test_ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDfjTM6KSLm6fVYjLNYosPupbjDwavf6thtHje+pBg0QLgn9hR2W0kiHRoomMIc8OBVoYk8xzQOQDGlx4uoobdQwiONwEqAzdisKVsZSW1mejuBWpxxkzTQx3rVtAmy3bSspiGIqwFWbKAiWoHTvSq6XXriHrs4iZX1f9cnp6AE0FdG3xWYpYlC3wmeK010F/9U2RVYTMikUyPj8CPmNmH0E00f00Nlk43EjwITpcNt5nzzL8Mvet7c2Bh4udp2WVItnK0Jh4G1yYxKg7835vcRzVRwJiARbA9i7+9fzmHZHWEJucSw04M98pPdWyokBHpdRj8hBTXgjh5+wN92SVwL"
    test_ssh_private_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA340zOiki5un1WIyzWKLD7qW4w8Gr3+rYbR43vqQYNEC4J/YU\ndltJIh0aKJjCHPDgVaGJPMc0DkAxpceLqKG3UMIjjcBKgM3YrClbGUltZno7gVqc\ncZM00Md61bQJst20rKYhiKsBVmygIlqB070qul164h67OImV9X/XJ6egBNBXRt8V\nmKWJQt8JnitNdBf/VNkVWEzIpFMj4/Aj5jZh9BNNH9NDZZONxI8CE6XDbeZ88y/D\nL3re3NgYeLnadllSLZytCYeBtcmMSoO/N+b3Ec1UcCYgEWwPYu/vX85h2R1hCbnE\nsNODPfKT3VsqJAR6XUY/IQU14I4efsDfdklcCwIDAQABAoIBADvf5LWSKP/x772M\nychWp+W2SztbFv69NsRbEJEmADmWj/xcA3UD1B2n78apy2vW9C7bOhemPwIGHYYK\nYRSEY8XkiYNA2nOPLpZF6Vlnej61RFTMARTGWaIFm5e7RdG7YdXQFTE2pAASzf0F\ngrpEczpBKVWA56In75s2Z1j+o3RGHIgBjnuVC1pK0JV+84jvaV5SWTHGWqqxGLnP\nQNtDKqGeNvmrrYq1u/f9K+tQRl5MJw14NlI+NluQaTgfcG8wE/BlGqCjALUiZLh4\nqEwNKs7Eh2b0qJjUJGvpiITdzJ1qzF7VaZWpWKqW7ws+vujn7hf+exAkgI1UBvY9\nS9W0JpkCgYEA/i/FX2AxyUuOJ/huly4fnI5dEKNQGNIj06xwga7JdsEXAUceMHvB\nzwL9eRwg0dKW6mQqc2z3gGvdb5CsKbC1C0UQ87tUMUf5XIknakQ3Uai8DiolpnUl\nUOgq2T9s7zRm/0atSFE/upUhhbfbAo/xXIn+8DG43KGZiHNJN5J+nn8CgYEA4SV6\nuFkKZKI2qRWmaXk4etfueCBKhG6IdjIpNhwBpusK/Rtka0ZLg9bUnCreP6sryrbR\nVfdUgB62P12ugSyKsbA/10P/K3/PFIr0kTRNhjrb85KkWhYiAJcBhJU56sWflu1r\nbJeJ5AzE9J8FWgfrwNJZ8kVd/FEL1FS03Y93FHUCgYEAj6wKwJ0Lpv6YzEjkoXkF\njyT8v3G/zTfB3lwif3p/DyuWyDcdfkQFSPAkuzbF6jNA8B1LzVAzGRhe4jeAyFPE\nESmpqkohDXXkIYS4jZ0fM33PRaZW/55JSFDiH0d1WENjUDjvqueZwOmYOA+yr+ES\niL7LJZLFLZf9wx1+rfWUshsCgYAXorefYrmUlvLmDT/LEs67FrASLFGmVXQ99EYf\nSBFkVIhyyc1g9aA31vW670UlqfKO9WJEhBJ64L6BKHSJWwO0Y6xQDPNcva4fmfbS\nx4rb7JHqoBpg2rH3HeMq5/+MhfKbBZGhdMclCbIjfA4zxWEafPq0VFPpiRiU0c+q\n8sStgQKBgQCNnh+y4QppC8UW8irxjZHNCuv+CUlHOjHhm82WHUm1flvDtIxHW3S8\nUKyhS4c9AgIywA7DXxSize7HpSZb3DqWg0DIq7FnRuHykLqPF0PiCMCi1sGWfp31\nMMLk7skCAIkXKyclGYQamgtuj87I13ZHnZYM4DwYgiklLXf8F5J4qw==\n-----END RSA PRIVATE KEY-----\n"

    # fix ids to ensure repos are kept across tests within the same run
    main_branch_name = "main"

    repo: Repository
    workspace: Workspace
    test_branch: Branch

    def __init__(self):
        # Set up initial data
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.workspace = Workspace.objects.create(
            id=TEST_WORKSPACE_ID,
            name="Test workspace",
        )
        self.workspace.users.add(self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        ssh_key = SSHKey.objects.create(
            workspace=self.workspace,
            public_key=self.test_ssh_public_key,
            private_key=self.test_ssh_private_key,
        )
        self.repo = Repository.objects.create(
            workspace=self.workspace,
            main_branch_name=self.main_branch_name,
            ssh_key=ssh_key,
            git_repo_url=self.git_repo_url,
        )
        self.test_branch = Branch.objects.create(
            workspace=self.workspace,
            repository=self.repo,
            branch_name="test-branch",
        )


isolate_mark = pytest.mark.parametrize("isolate", [True, False])


@pytest.mark.django_db
class TestGitConnections:
    @pytest.fixture
    def conn(self):
        return GitConnectionHelper()

    @pytest.fixture(scope="session", autouse=True)
    def run_command_after_tests(request):
        yield
        # This will run after all tests are completed
        path_to_delete = os.path.join(settings.MEDIA_ROOT, "ws", TEST_WORKSPACE_ID)
        if os.path.exists(path_to_delete):
            shutil.rmtree(path_to_delete)

    def test_repo_connection(
        self,
        conn: GitConnectionHelper,
    ):
        res = conn.repo.test_repo_connection()
        assert res["success"]

    @isolate_mark
    def test_repo_context(self, conn: GitConnectionHelper, isolate):
        with conn.repo.main_branch.repo_context(isolate=isolate) as (repo, _):
            assert len(os.listdir(repo.working_tree_dir)) > 3

    @isolate_mark
    def test_dbt_repo_context(self, conn: GitConnectionHelper, isolate):
        bigquery_resource = Resource.objects.create(
            type=ResourceType.DB,
            workspace=conn.workspace,
        )
        gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        BigqueryDetails(
            resource=bigquery_resource,
            lookback_days=1,
            schema_include=["analytics", "analytics-mini"],
            service_account=json.loads(gac.replace("\n", "\\n")),
        ).save()

        details = DBTCoreDetails.objects.create(
            resource=bigquery_resource,
            repository=conn.repo,
            project_path=".",
            threads=1,
            version=DBTVersion.V1_6.value,
            database="test",
            schema="test",
        )
        with details.dbt_repo_context(isolate=isolate) as (project, filepath, _):
            assert project != None
            assert filepath != None

    @isolate_mark
    def test_clone_repo_if_not_exists(self, conn: GitConnectionHelper, isolate):
        with conn.repo.main_branch.repo_context(isolate=isolate) as (repo, _):
            assert repo.active_branch.name == conn.repo.main_branch_name

    @isolate_mark
    def test_get_repo_if_already_exists(self, conn: GitConnectionHelper, isolate):
        with conn.repo.main_branch.repo_context(isolate=isolate) as (repo, _):
            assert repo is not None

            with conn.repo.main_branch.repo_context(
                isolate=isolate, repo_override=repo
            ) as (repo2, _):
                assert repo2 is not None

    @isolate_mark
    def test_get_working_tree(self, conn: GitConnectionHelper, isolate):
        with conn.repo.main_branch.repo_context(isolate=isolate) as (repo, _):
            assert repo.working_tree_dir is not None

    @isolate_mark
    def test_switch_branch(self, conn: GitConnectionHelper, isolate):
        with conn.test_branch.repo_context(isolate=isolate) as (repo, env):
            assert (
                conn.test_branch.switch_to_git_branch(isolate, repo, env)
                == conn.test_branch.branch_name
            )

    @isolate_mark
    def create_branch(self, conn: GitConnectionHelper, isolate):
        branch_name = "test_branch" + "".join([hex(x)[2:] for x in os.urandom(32)])
        branch = Branch.objects.create(
            workspace=conn.workspace,
            repository=conn.repo,
            branch_name=branch_name,
        )
        try:
            assert branch.create_git_branch(isolate=isolate) == branch_name
        finally:
            branch.delete_files()

    @isolate_mark
    def test_pull(self, conn: GitConnectionHelper, isolate):
        assert conn.test_branch.git_pull(isolate=isolate)

    @isolate_mark
    def test_commit_and_push(self, conn: GitConnectionHelper, isolate):
        branch = conn.test_branch
        with branch.repo_context(isolate=isolate) as (repo, env):
            assert branch.switch_to_git_branch(isolate, repo, env) == branch.branch_name
            path = os.path.join(repo.working_tree_dir, "README.md")
            with open(path, "a") as f:
                f.write("\n" + "".join([hex(x)[2:] for x in os.urandom(32)]))
            assert repo.is_dirty(untracked_files=True)

            assert branch.git_commit_and_push(
                "Add random hex string to README.md", isolate, repo, env
            )

            assert not repo.is_dirty(untracked_files=True)
