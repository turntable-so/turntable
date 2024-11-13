from __future__ import annotations

import logging
import os
import tempfile
import uuid
from contextlib import contextmanager

from django.db import models, transaction
from git import Repo as GitRepo
from git.exc import GitCommandError

from app.models.workspace import Workspace

from .ssh_key import SSHKey

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
        with self.main_project.repo_context() as (repo, env):
            return [ref.remote_head for ref in repo.remote().refs]

    @property
    def repo_name(self):
        return self.git_repo_url.split("/")[-1].split(".")[0]

    @transaction.atomic
    def save(self, *args, **kwargs):
        from app.models.project import Project

        # save repo
        super().save(*args, **kwargs)

        # create main branch
        Project.objects.get_or_create(
            name=self.main_branch_name + " (read only)",
            read_only=True,
            repository=self,
            branch_name=self.main_branch_name,
            workspace=self.workspace,
        )

    # override main branch id. Useful for tests
    def save_with_main_project_id(self, main_project_id: str, *args, **kwargs):
        from app.models.project import Project

        # save repo
        super().save(*args, **kwargs)

        # create main branch
        Project.objects.get_or_create(
            id=main_project_id,
            name=self.main_branch_name + " -- readonly",
            read_only=True,
            repository=self,
            branch_name=self.main_branch_name,
            workspace=self.workspace,
        )

    @property
    def main_project(self):
        return self.projects.get(
            branch_name=self.main_branch_name,
            workspace=self.workspace,
        )

    def get_project(self, project_id: str):
        return self.projects.get(id=project_id, workspace=self.workspace)

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
