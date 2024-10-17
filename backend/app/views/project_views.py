import os
import shlex
import shutil
from urllib.parse import unquote

from django.http import StreamingHttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import AssetSerializer, LineageSerializer
from app.core.dbt import LiveDBTParser
from app.models.git_connections import Branch
from workflows.dbt_runner import DBTStreamerWorkflow
from asgiref.sync import sync_to_async


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
        with dbt_details.dbt_repo_context() as (project, project_path, repo):
            filepath = request.query_params.get("filepath")
            if filepath and len(filepath) > 0:
                filepath = os.path.join(project_path, unquote(filepath))
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

            root = get_file_tree(user_id, repo.working_tree_dir, project_path)
            dirty_changes = repo.index.diff(None)

        return Response(
            {
                "file_index": [root],
                # "dirty_changes": dirty_changes,
            }
        )

    @action(detail=False, methods=["GET", "POST", "PATCH"])
    def branches(self, request):
        workspace = request.user.current_workspace()
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

    @action(detail=False, methods=["GET"])
    def lineage(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_details()
        filepath = unquote(request.query_params.get("filepath"))
        predecessor_depth = int(request.query_params.get("predecessor_depth"))
        successor_depth = int(request.query_params.get("successor_depth"))
        lineage_type = request.query_params.get("lineage_type", "all")
        defer = request.query_params.get("defer", True)
        branch_name = request.query_params.get("branch_name")
        if branch_name:
            try:
                branch_id = Branch.objects.get(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=branch_name,
                ).id
            except Branch.DoesNotExist:
                return Response(
                    {"error": f"Branch {branch_name} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            branch_id = None

        with dbt_details.dbt_transition_context(branch_id=branch_id) as (
            transition,
            _,
            repo,
        ):
            transition.mount_manifest(defer=defer)
            transition.mount_catalog(defer=defer)

            node_id = LiveDBTParser.get_node_id_from_filepath(
                transition.after, filepath, defer
            )
            if not node_id:
                raise ValueError(f"Node at filepath{filepath} not found in manifest")

            dbtparser = LiveDBTParser.parse_project(
                proj=transition.after,
                before_proj=transition.before,
                node_id=node_id,
                resource=dbt_details.resource,
                predecessor_depth=predecessor_depth,
                successor_depth=successor_depth,
                defer=defer,
            )
            lineage, _ = dbtparser.get_lineage()
            root_asset = None
            column_lookup = {}
            for asset in lineage.assets:
                column_lookup[asset.id] = []
            for column in lineage.columns:
                column_lookup[column.asset_id].append(column)

            for asset in lineage.assets:
                if asset.id == lineage.asset_id:
                    root_asset = asset

                asset.temp_columns = column_lookup[asset.id]

            if not root_asset:
                raise ValueError(f"Root asset not found for {lineage.asset_id}")

            asset_serializer = AssetSerializer(root_asset, context={"request": request})
            lineage_serializer = LineageSerializer(
                lineage, context={"request": request}
            )
            return Response(
                {
                    "root_asset": asset_serializer.data,
                    "lineage": lineage_serializer.data,
                }
            )
