import logging
import os
import subprocess
from random import randint

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import SSHKey
from app.services.code_repo_service import CodeRepoService
from app.services.github_service import GithubService

logger = logging.getLogger(__name__)


class SSHViewSet(APIView):

    def get(self, request):
        action = request.query_params.get("action")
        workspace_id = request.query_params.get("tenant_id")

        logger.debug(f"Received action: {action}, tenant_id: {workspace_id}")

        repo_service = CodeRepoService(workspace_id)

        if action == "generate_ssh_key":
            resp = repo_service.generate_deploy_key()
            return Response(resp, status=201)
        else:
            return Response({"error": "Invalid action"}, status=400)

    def post(self, request):
        action = request.data.get("action")
        logger.debug(f"Received action: {action}")
        coderepo_service = CodeRepoService(
            workspace_id=request.user.current_workspace().id
        )

        if action == "test_git_connection":
            print(request.data, flush=True)
            result = coderepo_service.test_repo_connection(
                public_key=request.data.get("public_key"),
                git_repo_url=request.data.get("git_repo_url"),
            )
            return Response(result)
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
