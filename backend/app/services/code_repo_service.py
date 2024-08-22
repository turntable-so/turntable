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

from app.models import SSHKey

logger = logging.getLogger(__name__)


class CodeRepoService:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

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
