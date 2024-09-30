import os

from django.http import JsonResponse
from app.services.code_repo_service import CodeRepoService
from workflows.hatchet import hatchet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from urllib.parse import unquote
from asgiref.sync import sync_to_async
import shutil


class ProjectViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["GET", "POST", "PUT", "DELETE"])
    def files(self, request):
        workspace = request.user.current_workspace()
        user_id = request.user.id
        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_details()
        service = CodeRepoService(workspace.id)
        repo = service.get_repo(
            user_id, dbt_details.deploy_key, dbt_details.git_repo_url
        )

        filepath = request.query_params.get("filepath")
        if filepath and len(filepath) > 0:
            filepath = unquote(filepath)
            filepath = os.path.join(repo.working_tree_dir, filepath)
            if request.method == "POST":
                if os.path.exists(filepath):
                    return Response(
                        {"error": "file already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w") as file:
                    file.write(request.data.get("contents"))
                return Response(status=status.HTTP_201_CREATED)

            if not os.path.exists(filepath):
                return Response(status=status.HTTP_404_NOT_FOUND)

            if request.method == "GET":
                with open(filepath, "r") as file:
                    file_content = file.read()
                return Response({"contents": file_content})

            if request.method == "PUT":
                with open(filepath, "w") as file:
                    file.write(request.data.get("contents"))
                return Response(status=status.HTTP_204_NO_CONTENT)

            if request.method == "DELETE":
                if filepath and len(filepath) > 0:
                    filepath = os.path.join(repo.working_tree_dir, filepath)
                    if os.path.exists(filepath):
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                        elif os.path.isdir(filepath):
                            shutil.rmtree(filepath)
                        else:
                            return Response(
                                {"error": "Path is neither a file nor a directory"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        return Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response(
                            {"error": "File or directory not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

        file_tree = service.get_file_tree(user_id, repo.working_tree_dir)
        dirty_changes = repo.index.diff(None)

        return Response(
            {
                "file_index": file_tree,
                "dirty_changes": dirty_changes,
            }
        )

    @action(detail=False, methods=["GET", "POST", "PATCH"])
    def branches(self, request):
        workspace = request.user.current_workspace()
        user_id = request.user.id
        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )
        service = CodeRepoService(workspace.id)
        repo = service.get_repo(
            user_id, dbt_details.deploy_key, dbt_details.git_repo_url
        )
        if request.method == "GET":
            return Response(
                {
                    "active_branch": repo.active_branch.name,
                    "branches": [branch.name for branch in repo.branches],
                }
            )
        elif request.method == "POST":
            # Implement POST logic here
            if not request.data.get("branch_name"):
                return Response(
                    {"error": "Branch name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            branch_name = service.create_branch(
                user_id,
                dbt_details.git_repo_url,
                dbt_details.deploy_key,
                request.data.get("branch_name"),
            )
            return Response(
                {"branch_name": branch_name}, status=status.HTTP_201_CREATED
            )

        elif request.method == "PATCH":
            if not request.data.get("branch_name"):
                return Response(
                    {"error": "Branch name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            branch_name = service.switch_branch(
                user_id,
                dbt_details.git_repo_url,
                dbt_details.deploy_key,
                request.data.get("branch_name"),
            )
            return Response({"branch_name": branch_name})

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
