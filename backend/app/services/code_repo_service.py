import logging
import os
import subprocess
import tempfile
from contextlib import contextmanager
from random import randint

import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from git import Repo
from git.exc import GitCommandError

from app.models import SSHKey
from django.conf import settings

logger = logging.getLogger(__name__)


class CodeRepoService:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

    def _generate_code_repo_path(self, user_id: str):
        path = os.path.join(f"/ws/{self.workspace_id}/users/{user_id}")
        return os.path.join(settings.MEDIA_ROOT, path)

    def _generate_ssh_rsa(self):
        # Generate a new RSA key pair
        key = rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537, key_size=2048
        )

        # Serialize the public key
        public_key = key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )

        private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        return public_key.decode("utf-8"), private_key.decode("utf-8")

    def generate_deploy_key(self):
        if SSHKey.objects.filter(workspace_id=self.workspace_id).exists():
            logger.debug(f"SSH keys already exist for {self.workspace_id}")
            ssh_key = SSHKey.objects.filter(workspace_id=self.workspace_id).first()
            return {
                "public_key": ssh_key.public_key,
            }
        else:
            public_key, private_key = self._generate_ssh_rsa()
            ssh_key = SSHKey.objects.create(
                workspace_id=self.workspace_id,
                public_key=public_key,
                private_key=private_key,
            )
            logger.debug(f"SSH keys generated successfully for {self.workspace_id}")
            return {
                "public_key": ssh_key.public_key,
            }

    def _run_ssh_command(self, public_key: str, git_repo_url: str, command: list):
        key = SSHKey.objects.filter(public_key=public_key).first()
        if not key:
            raise ValueError("Invalid public key")

        ssh_key_text = key.private_key
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

    def test_repo_connection(self, public_key: str, git_repo_url: str):
        return self._run_ssh_command(
            public_key=public_key,
            git_repo_url=git_repo_url,
            command=["git", "ls-remote", git_repo_url],
        )

    @contextmanager
    def repo_context(self, public_key: str, git_repo_url: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            self._run_ssh_command(
                public_key=public_key,
                git_repo_url=git_repo_url,
                command=["git", "clone", git_repo_url, temp_dir],
            )

            yield temp_dir

    @contextmanager
    def with_ssh_env(self, public_key: str):
        key = SSHKey.objects.filter(public_key=public_key).first()
        if not key:
            raise ValueError("Invalid public key")

        temp_key_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        try:
            temp_key_file.write(key.private_key)
            temp_key_file.close()
            os.chmod(temp_key_file.name, 0o400)

            git_ssh_cmd = f"ssh -i {temp_key_file.name} -o StrictHostKeyChecking=no"
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = git_ssh_cmd

            yield env
        finally:
            os.remove(temp_key_file.name)

    def get_repo(self, user_id: str, public_key: str, git_repo_url: str) -> Repo:
        path = self._generate_code_repo_path(user_id)

        if os.path.exists(path):
            return Repo(path)

        key = SSHKey.objects.filter(public_key=public_key).first()
        if not key:
            raise ValueError("Invalid public key")

        with self.with_ssh_env(public_key) as env:
            repo = Repo.clone_from(git_repo_url, path, env=env)

        return repo

    def create_branch(
        self, user_id: str, git_repo_url: str, public_key: str, branch_name: str
    ) -> str:
        with self.with_ssh_env(public_key) as env:
            repo = self.get_repo(user_id, public_key, git_repo_url)
            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)
            # Create and checkout the new branch
            try:
                new_branch = repo.create_head(branch_name)
                new_branch.checkout()

                # Push the new branch to the remote
                repo.git.push("--set-upstream", "origin", branch_name, env=env)

                return branch_name
            except GitCommandError as e:
                # Handle errors (e.g., branch already exists)
                print(f"Error creating branch: {e}")
                return None

    def switch_branch(
        self, user_id: str, git_repo_url: str, public_key: str, branch_name: str
    ) -> str:
        with self.with_ssh_env(public_key) as env:
            repo = self.get_repo(user_id, public_key, git_repo_url)

            # Fetch the latest changes from the remote
            repo.remotes.origin.fetch(env=env)

            try:
                # Check if the branch exists locally
                if branch_name in repo.heads:
                    branch = repo.heads[branch_name]
                else:
                    # If not, create a new branch tracking the remote branch
                    branch = repo.create_head(branch_name, f"origin/{branch_name}")
                    branch.set_tracking_branch(repo.remotes.origin.refs[branch_name])

                # Checkout the branch
                branch.checkout()

                return branch_name
            except GitCommandError as e:
                # Handle errors (e.g., branch doesn't exist)
                print(f"Error switching branch: {e}")
                return None

    def commit_and_push(
        self, user_id: str, public_key: str, git_repo_url: str, commit_message: str
    ) -> bool:
        with self.with_ssh_env(public_key) as env:
            repo = self.get_repo(user_id, public_key, git_repo_url)

            try:
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
                    repo.head.commit, repo.remotes.origin.refs[current_branch].commit
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
            except GitCommandError as e:
                print(f"Error committing and pushing changes: {e}")
                return False

    def pull(self, user_id: str, public_key: str, git_repo_url: str):
        with self.with_ssh_env(public_key) as env:
            repo = self.get_repo(user_id, public_key, git_repo_url)

            # Check if the working directory is clean
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
