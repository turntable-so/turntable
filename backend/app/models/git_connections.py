from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from random import randint

from django.conf import settings
from django.db import models, transaction
from git import Repo as GitRepo
from git.exc import GitCommandError

from app.models.workspace import Workspace
from app.utils.fields import encrypt

logger = logging.getLogger(__name__)


class SSHKey(models.Model):
    # pk
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # fields
    public_key = models.TextField()
    private_key = encrypt(models.TextField())

    # relationships
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    @classmethod
    def generate_deploy_key(cls, workspace_id: str):
        try:
            ssh_key = SSHKey.objects.get(workspace_id=workspace_id)
            logger.debug(f"SSH keys already exist for {cls.workspace_id}")
        except SSHKey.DoesNotExist:
            public_key, private_key = cls._generate_ssh_rsa()
            ssh_key = SSHKey.objects.create(
                workspace_id=cls.workspace_id,
                public_key=public_key,
                private_key=private_key,
            )
            logger.debug(f"SSH keys generated successfully for {cls.workspace_id}")

        return {
            "public_key": ssh_key.public_key,
        }


class Repository(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    main_branch_name = models.CharField(max_length=255, null=False)
    git_repo_url = models.URLField(null=False)

    # relationships
    ssh_key = models.ForeignKey(SSHKey, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

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

    def _run_ssh_command(self, command: list):
        ssh_key_text = self.ssh_key.private_key
        private_key_path = str(randint(1000, 9999)) + ".pem"

        # Load the SSH key from the text
        with open(private_key_path, "w") as f:
            f.write(ssh_key_text)

        try:
            subprocess.run(["chmod", "600", private_key_path], check=True)
            ssh_agent = subprocess.Popen(["ssh-agent", "-s"], stdout=subprocess.PIPE)
            agent_output = ssh_agent.communicate()[0].decode("utf-8")

            # Extract the SSH agent PID and socket
            agent_info = dict(
                line.split("=") for line in agent_output.split(";") if "=" in line
            )
            os.environ["SSH_AUTH_SOCK"] = agent_info.get("SSH_AUTH_SOCK", "").strip()
            os.environ["SSH_AGENT_PID"] = agent_info.get("SSH_AGENT_PID", "").strip()

            # Add the SSH key to the agent
            subprocess.run(["ssh-add", private_key_path], check=True)

            # Set up the SSH command for git
            git_command = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}"
            os.environ["GIT_SSH_COMMAND"] = git_command

            # Execute the git ls-remote command
            answer = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            stdout = answer.stdout
            stderr = answer.stderr
            returncode = answer.returncode
            result = stdout if returncode == 0 else stderr

            if returncode != 0:
                return {"success": False, "error": result}
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            os.remove(private_key_path)

    def test_repo_connection(self):
        return self._run_ssh_command(command=["git", "ls-remote", self.git_repo_url])

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
    branch_name = models.CharField(max_length=255)

    # relationships
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="branches"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    @property
    def is_main(self):
        return self.branch_name == self.repository.main_branch_name

    @contextmanager
    def _code_repo_path(self, isolate: bool = False):
        path = os.path.join(
            "ws",
            str(self.workspace.id),
            str(self.repository.id),
            str(self.id),
        )
        if not isolate:
            yield os.path.join(settings.MEDIA_ROOT, path)
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            yield os.path.join(temp_dir, path)

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
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> str:
        with self.repo_context(isolate, repo_override, env_override) as (repo, env):
            # Fetch the latest changes from the remoteå
            repo.remotes.origin.fetch(env=env)
            remote_names = [r.remote_name for r in repo.remotes.origin.refs]
            if self.branch_name in remote_names:
                raise ValueError(f"Branch {self.branch_name} already exists")

            # Create and checkout the new branch
            new_branch = repo.create_head(self.branch_name)
            new_branch.checkout()

            # Push the new branch to the remote and set tracking branch
            repo.git.push("--set-upstream", "origin", self.branch_name, env=env)

            return self.branch_name

    def switch_to_git_branch(
        self,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> str:
        with self.repo_context(isolate, repo_override, env_override) as (repo, env):
            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)
            repo.git.checkout(self.branch_name, env=env)
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

    def git_commit_and_push(
        self,
        commit_message: str,
        isolate: bool = False,
        repo_override: GitRepo | None = None,
        env_override: dict[str, str] | None = None,
    ) -> bool:
        with self.repo_context(
            isolate=isolate,
            repo_override=repo_override,
            env_override=env_override,
        ) as (repo, env):
            # Check if there are any changes to commit
            if not repo.is_dirty(untracked_files=True):
                print("No changes to commit.")
                return False

            # Add all changes
            repo.git.add(A=True)
            # Commit changes
            repo.index.commit(commit_message)

            # Get the current branch name
            current_branch = repo.active_branch.name

            # Fetch the latest changes from remote
            repo.remotes.origin.fetch(env=env)

            # Check if local branch is behind remote
            if repo.is_ancestor(
                repo.head.commit,
                repo.remotes.origin.refs[current_branch].commit,
            ):
                # If behind, attempt to rebase
                try:
                    repo.git.rebase(f"origin/{current_branch}", env=env)
                except GitCommandError:
                    # If rebase fails, abort and return False
                    repo.git.rebase("--abort")
                    print("Failed to rebase. Please resolve conflicts manually.")
                    return False

            # Push changes to remote
            origin = repo.remote(name="origin")
            origin.push(current_branch, env=env)

            print(f"Changes committed and pushed to branch '{current_branch}'.")
            return True

    def delete_files(self, isolate: bool = False):
        with self._code_repo_path(isolate) as path:
            if os.path.exists(path):
                shutil.rmtree(path)
