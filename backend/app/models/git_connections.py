from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from random import randint

from django.conf import settings
from django.db import models
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

    def save(self, *args, **kwargs):
        # create main branch
        Branch.objects.get_or_create(
            repo=self, branch_name=self.main_branch_name, workspace=self.workspace
        )
        # save repo
        super().save(self, *args, **kwargs)

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
    def with_ssh_env(self):
        temp_key_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        try:
            temp_key_file.write(self.ssh_key.private_key)
            temp_key_file.close()
            os.chmod(temp_key_file.name, 0o400)

            git_ssh_cmd = f"ssh -i {temp_key_file.name} -o StrictHostKeyChecking=no"
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = git_ssh_cmd

            yield env
        finally:
            os.remove(temp_key_file.name)


class Branch(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    branch_name = models.CharField(max_length=255)

    # relationships
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)

    @property
    def is_main(self):
        return self.branch_name == self.repo.main_git_branch

    def get_repo(self) -> GitRepo:
        path = self._generate_code_repo_path()

        if os.path.exists(path):
            return GitRepo(path)

        with self.with_ssh_env() as env:
            repo = GitRepo.clone_from(self.repo.git_repo_url, path, env=env)

            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)

            # check if branch already exists in git, and create if not
            if self.branch_name not in repo.heads:
                self._create_git_branch(repo, env)

            # switch to the branch
            self._switch_git_branch(repo, env)

        return repo

    def _generate_code_repo_path(self):
        path = os.path.join(
            "ws",
            str(self.workspace_id),
            str(self.repo.id),
            str(self.id),
        )
        if os.environ["EPHEMERAL_FILESYSTEM"] == "True":
            return os.path.join(tempfile.gettempdir(), path)

        return os.path.join(settings.MEDIA_ROOT, path)

    def _create_git_branch(self, repo: GitRepo, ssh_env=None) -> str:
        if ssh_env is None:
            ssh_env = self.repo.with_ssh_env()
        with ssh_env as env:
            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)
            # Create and checkout the new branch
            try:
                new_branch = repo.create_head(self.branch_name)
                repo.set_tracking_branch(repo.remotes.origin.refs[self.branch_name])
                new_branch.checkout()
                # Push the new branch to the remote
                repo.git.push("--set-upstream", "origin", self.branch_name, env=env)
                return self.branch_name
            except GitCommandError as e:
                # Handle errors (e.g., branch already exists)
                print(f"Error creating branch: {e}")
                return None

    def _switch_git_branch(self, repo: GitRepo, ssh_env=None) -> str:
        if ssh_env is None:
            ssh_env = self.repo.with_ssh_env()

        with ssh_env as env:
            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)

            try:
                branch = repo.heads[self.branch_name]
                branch.checkout()
                return self.branch_name
            except GitCommandError as e:
                # Handle errors (e.g., branch doesn't exist)
                print(f"Error switching branch: {e}")
                return None

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]
