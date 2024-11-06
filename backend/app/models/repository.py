from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
import uuid

import django.utils.timezone

from app.models.user import User

from .ssh_key import SSHKey
from app.models.workspace import Workspace
from django.db import models, transaction

import logging
import os
import shutil
import tempfile
import uuid
from contextlib import contextmanager

from django.conf import settings
from django.db import models
from git import Repo as GitRepo
from git.exc import GitCommandError
from app.models.workspace import Workspace

logger = logging.getLogger(__name__)


class Repository(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    main_branch_name = models.CharField(max_length=255, null=False, default="main")
    git_repo_url = models.CharField(max_length=255, null=False)

    # relationships
    ssh_key = models.ForeignKey(SSHKey, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    def get_remote_branches(self):
        with self.main_branch.repo_context() as (repo, env):
            return [ref.remote_head for ref in repo.remote().refs]

    @property
    def repo_name(self):
        return self.git_repo_url.split("/")[-1].split(".")[0]

    @transaction.atomic
    def save(self, *args, **kwargs):
        # save repo
        super().save(*args, **kwargs)

        # create main branch
        Branch.objects.get_or_create(
            repository=self, branch_name=self.main_branch_name, workspace=self.workspace
        )

    # override main branch id. Useful for tests
    def save_with_main_branch_id(self, main_branch_id: str, *args, **kwargs):
        # save repo
        super().save(*args, **kwargs)

        # create main branch
        Branch.objects.get_or_create(
            id=main_branch_id,
            repository=self,
            branch_name=self.main_branch_name,
            workspace=self.workspace,
        )

    @property
    def main_branch(self) -> Branch:
        return self.branches.get(
            branch_name=self.main_branch_name,
            workspace=self.workspace,
        )

    def get_branch(self, branch_id: str) -> Branch:
        return self.branches.get(id=branch_id, workspace=self.workspace)

    @property
    def remote_branches(self):
        with self.with_ssh_env() as env:
            with tempfile.TemporaryDirectory() as tmp_dir:
                repo = GitRepo.init(tmp_dir)
                # Get the raw ls-remote output and parse it
                ls_remote_output = repo.git.ls_remote(
                    "--heads", self.git_repo_url, env=env
                )
                # Convert the output to a list of branch names
                branches = []
                for line in ls_remote_output.split("\n"):
                    if line.strip():
                        # Each line is in format: "<commit-hash>\trefs/heads/<branch-name>"
                        branch_name = line.split("refs/heads/")[-1]
                        branches.append(branch_name)
                return branches

    # used before project is created
    def test_remote_repo_connection(self):
        with self.with_ssh_env() as env:
            with tempfile.TemporaryDirectory() as tmp_dir:
                try:
                    repo = GitRepo.init(tmp_dir)
                    repo.git.ls_remote(self.git_repo_url, env=env)
                    return {
                        "success": True,
                        "result": "Repository connection successful",
                    }
                except GitCommandError as e:
                    return {
                        "success": False,
                        "error": f"Failed to connect to the repository. {str(e)}",
                    }

    @contextmanager
    def with_ssh_env(self, env_override: dict[str, str] | None = None):
        if env_override is not None:
            yield env_override
            return

        with tempfile.NamedTemporaryFile(mode="w", suffix=".pem") as temp_key_file:
            temp_key_file.write(self.ssh_key.private_key)
            temp_key_file.flush()
            os.chmod(temp_key_file.name, 0o400)

            git_ssh_cmd = f"ssh -i {temp_key_file.name} -o StrictHostKeyChecking=no"
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = git_ssh_cmd

            yield env


class Branch(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    branch_name = models.CharField(max_length=255, null=False)
    read_only = models.BooleanField(default=False)

    # relationships
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="branches"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["branch_name", "repository", "workspace"]

    @property
    def is_main(self):
        return self.branch_name == self.repository.main_branch_name

    @property
    def is_cloned(self):
        with self._code_repo_path() as path:
            return os.path.exists(path)

    @property
    def pull_request_url(self):
        if not self.repository.git_repo_url:
            return None
        # Parse git URL into GitHub format
        url = self.repository.git_repo_url
        if url.startswith("git@"):
            # Convert SSH format to HTTPS
            url = url.replace(":", "/").replace("git@", "https://")

        if url.endswith(".git"):
            url = url[:-4]
        return f"{url}/pull/new/{self.branch_name}"

    def clone(self):
        with self._code_repo_path() as path:
            if os.path.exists(path) and ".git" in os.listdir(path):
                raise Exception("Repository already cloned")

            with self.repository.with_ssh_env() as env:
                repo = GitRepo.clone_from(self.repository.git_repo_url, path, env=env)

                # Fetch the latest changes from the remote
                repo.remotes.origin.fetch(env=env)

                # switch to the branch
                self.switch_to_git_branch(repo_override=repo, env_override=env)

        return True

    def commit(self, commit_message: str, file_paths: list[str]):
        with self._code_repo_path() as repo_path:
            with self.repository.with_ssh_env() as env:
                repo = GitRepo(repo_path)
                # Add each specified file
                print(os.listdir(repo_path), flush=True)
                for file_path in file_paths:
                    repo.git.add(os.path.join(repo.working_tree_dir, file_path))
                # Commit the changes
                repo.git.commit(m=commit_message, env=env)
                # Push to remote
                repo.git.push("origin", self.branch_name, env=env)

        return True

    def discard_changes(self):
        with self.repo_context() as (repo, env):
            # Reset all staged changes
            repo.index.reset()

            # Discard all unstaged changes
            repo.git.checkout("--", ".")

            # Clean untracked files and directories
            repo.git.clean("-fd")

        return True

    @contextmanager
    def _code_repo_path(self, isolate: bool = False):
        path = os.path.join(
            "ws",
            str(self.workspace.id),
            str(self.repository.id),
            str(self.id),
            self.repository.repo_name,
        )
        if isolate or os.getenv("FORCE_ISOLATE") == "true":
            with tempfile.TemporaryDirectory() as temp_dir:
                yield os.path.join(temp_dir, path)
        else:
            yield os.path.join(settings.MEDIA_ROOT, path)

    @contextmanager
    def repo_context(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> tuple[GitRepo, dict[str, str] | None]:
        if repo_override is not None and env_override is not None:
            yield repo_override, env_override
            return

        elif repo_override is not None:
            with self.repository.with_ssh_env(env_override) as env:
                yield repo_override, env
                return

        with self._code_repo_path(isolate) as path:
            if os.path.exists(path) and ".git" in os.listdir(path):
                yield GitRepo(path), env_override
                return

            with self.repository.with_ssh_env(env_override) as env:
                repo = GitRepo.clone_from(self.repository.git_repo_url, path, env=env)

                # Fetch the latest changes from the remote
                repo.remotes.origin.fetch(env=env)

                # check if branch already exists in git, and create if not
                remote_branches = [ref.remote_head for ref in repo.remote().refs]
                if self.branch_name not in remote_branches:
                    self.create_git_branch(
                        isolate=isolate, repo_override=repo, env_override=env
                    )

                # switch to the branch
                self.switch_to_git_branch(
                    isolate=isolate, repo_override=repo, env_override=env
                )

                yield repo, env_override

    def create_git_branch(
        self,
        source_branch: str,
    ) -> str:
        with self.repository.with_ssh_env() as env:
            with tempfile.TemporaryDirectory() as tmp_dir:
                repo = GitRepo.init(tmp_dir)

                repo.git.fetch(
                    self.repository.git_repo_url,
                    f"{source_branch}:refs/remotes/origin/{source_branch}",
                    env=env,
                )

                # Create and checkout new branch
                repo.create_head(
                    self.branch_name, f"refs/remotes/origin/{source_branch}"
                )
                repo.git.push(
                    self.repository.git_repo_url, f"{self.branch_name}", env=env
                )

            return self.branch_name

    def git_pull(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> str:
        with self.repo_context(isolate, repo_override, env_override) as (
            repo,
            env,
        ):
            if repo.is_dirty(untracked_files=True):
                raise GitCommandError(
                    "DIRTY_WORKING_DIRECTORY",
                    "The working directory has uncommitted changes.",
                )

            # Fetch the latest changes
            repo.remotes.origin.fetch(env=env)

            # Get the current branch
            current_branch = repo.active_branch

            # Pull the latest changes
            repo.git.pull("origin", current_branch.name, env=env)

            return True
