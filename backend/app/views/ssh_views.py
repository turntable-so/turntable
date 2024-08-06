import logging
import os
import subprocess
from random import randint

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import SSHKey
from app.services.github_service import GithubService

logger = logging.getLogger(__name__)


class SSHViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        action = request.query_params.get("action")
        workspace_id = request.query_params.get("tenant_id")

        logger.debug(f"Received action: {action}, tenant_id: {workspace_id}")

        if action == "generate_ssh_key":
            return self.generate_ssh_key(workspace_id)
        else:
            return Response({"error": "Invalid action"}, status=400)

    def post(self, request):
        action = request.data.get("action")
        logger.debug(f"Received action: {action}")

        if action == "test_github_connection":
            return self.test_ssh_connection(request)
        else:
            return Response({"error": "Invalid action"}, status=400)

    def generate_ssh_key(self, workspace_id):
        if not workspace_id:
            logger.error("tenant_id is required but not provided.")
            return Response({"error": "tenant_id is required"}, status=400)

        try:
            github_service = GithubService(workspace_id)
            public_key, private_key = github_service.generate_ssh_rsa()

            SSHKey.objects.create(
                workspace_id=workspace_id,
                public_key=public_key,
                private_key=private_key,
            )
            logger.debug("SSH keys generated successfully.")
            return Response(
                {
                    "public_key": public_key,
                }
            )
        except ValueError as e:
            logger.error(f"Error generating SSH keys: {e}")
            return Response({"error": str(e)}, status=400)

    def test_ssh_connection(self, request):
        public_key_text = request.data.get("public_key")
        key = SSHKey.objects.filter(public_key=public_key_text).first()
        if not key:
            return Response({"error": "Invalid public key"}, status=400)

        ssh_key_text = key.private_key
        git_repo_url = request.data.get("github_url")
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
                ["git", "ls-remote", git_repo_url],
                capture_output=True,
                text=True,
                check=True,
            )

            stdout = answer.stdout
            stderr = answer.stderr
            returncode = answer.returncode
            result = stdout if returncode == 0 else stderr

            os.remove(private_key_path)

            if returncode != 0:
                return Response({"success": False, "error": result}, status=400)
            return Response({"success": True, "result": result})
        except Exception as e:
            os.remove(private_key_path)
            return Response({"success": False, "error": str(e)})
