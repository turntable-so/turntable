from rest_framework import status, viewsets
from rest_framework.response import Response

from api.serializers import GithubInstallationSerializer
from app.models import GithubInstallation


class GithubInstallationViewSet(viewsets.ModelViewSet):
    def create(self, request):
        workspace = request.user.current_workspace()
        deploy_key = request.data["deploy_key"]
        dbt_git_repo_url = request.data["dbt_git_repo_url"]
        git_repo_type = request.data["git_repo_type"]
        main_git_branch = request.data["main_git_branch"]
        name = request.data.get("name", None)

        installation = GithubInstallation.objects.create(
            workspace=workspace,
            user=request.user,
            ssh_key=deploy_key,
            git_url=dbt_git_repo_url,
            git_repo_type=git_repo_type,
            main_git_branch=main_git_branch,
            name=name,
        )

        serializer = GithubInstallationSerializer(
            installation, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        workspace = request.user.current_workspace()
        installations = GithubInstallation.objects.filter(workspace=workspace)
        serializer = GithubInstallationSerializer(installations, many=True)
        return Response(serializer.data)
