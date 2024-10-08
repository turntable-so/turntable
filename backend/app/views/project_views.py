import os

from django.http import JsonResponse
from app.models.git_connections import Branch
from workflows.hatchet import hatchet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from urllib.parse import unquote
from asgiref.sync import sync_to_async
import shutil


def _build_file_tree(user_id: str, path: str, base_path: str):
    tree = []
    for entry in os.scandir(path):
        if not entry.name.startswith("."):  # Exclude hidden files and directories
            relative_path = os.path.relpath(entry.path, base_path)
            node = {
                "path": relative_path,
                "type": "directory" if entry.is_dir() else "file",
                "name": entry.name,
                "id": relative_path,
            }
            if entry.is_dir():
                node["children"] = _build_file_tree(user_id, entry.path, base_path)
            tree.append(node)
    return tree


def get_file_tree(user_id: str, path: str, base_path: str):
    file_tree = _build_file_tree(user_id, path, base_path)
    relative_path = os.path.relpath(path, base_path)
    return {
        "path": path,
        "type": "directory",
        "name": os.path.basename(path),
        "id": relative_path,
        "children": file_tree,
    }


class ProjectViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["GET", "POST", "PUT", "DELETE"])
    def files(self, request):
        workspace = request.user.current_workspace()
        user_id = request.user.id
        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_details()
        with dbt_details.dbt_repo_context() as (project, _, repo):
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

            base_path = dbt_details.project_path

            root = get_file_tree(user_id, repo.working_tree_dir, base_path)
            dirty_changes = repo.index.diff(None)

        return Response(
            {
                "file_index": [root],
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

        with dbt_details.dbt_repo_context() as (project, _, repo):
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
                branch = Branch.objects.create(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                )
                branch.create_git_branch()

                return Response(
                    {"branch_name": branch.branch_name}, status=status.HTTP_201_CREATED
                )

            elif request.method == "PATCH":
                if not request.data.get("branch_name"):
                    return Response(
                        {"error": "Branch name is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                branch = Branch.objects.get(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                )
                with branch.repo_context() as (repo, env):
                    name = branch.switch_to_git_branch(repo, env)

                return Response({"branch_name": name})

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
