import logging

from app.models.git_connections import Repository
from app.models.workspace import Workspace
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import SSHKey
from app.services.github_service import GithubService

logger = logging.getLogger(__name__)


class SSHViewSet(APIView):
    def get(self, request):
        action = request.query_params.get("action")
        workspace = request.user.current_workspace()

        if action == "generate_ssh_key":
            key = SSHKey.generate_deploy_key(workspace)
            return Response(
                {
                    "public_key": key.public_key,
                },
                status=201,
            )
        else:
            return Response({"error": "Invalid action"}, status=400)

    def post(self, request):
        action = request.data.get("action")

        ssh_key = SSHKey.objects.get(public_key=request.data.get("public_key"))

        if action == "test_git_connection":
            repo = Repository(
                git_repo_url=request.data.get("git_repo_url"),
                ssh_key=ssh_key,
            )
            result = repo.test_repo_connection()
            return Response(result)
        else:
            return Response({"error": "Invalid action"}, status=400)
