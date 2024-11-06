import os
import shutil
from urllib.parse import unquote

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import AssetSerializer, LineageSerializer
from app.core.dbt import LiveDBTParser
from app.models.editor import Project


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
        dbt_details = workspace.get_dbt_dev_details()
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

        return Response(
            {
                "file_index": [root],
            }
        )

    @action(detail=False, methods=["GET"])
    def changes(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        with dbt_details.dbt_repo_context() as (project, _, repo):
            # Get untracked files
            untracked_files = []
            for filepath in repo.untracked_files:
                with open(os.path.join(repo.working_dir, filepath), "r") as file:
                    after_content = file.read()
                untracked_files.append(
                    {
                        "path": filepath,
                        "before": "",
                        "after": after_content,
                    }
                )

            # Get tracked modified files
            changed_files = []
            for item in repo.index.diff(None):
                with open(os.path.join(repo.working_dir, item.a_path), "r") as file:
                    after_content = file.read()
                before_content = repo.git.show(f"HEAD:{item.a_path}")
                changed_files.append(
                    {
                        "path": item.a_path,
                        "before": before_content,
                        "after": after_content,
                    }
                )

            # Get staged files
            staged_files = []
            for item in repo.index.diff("HEAD"):
                with open(os.path.join(repo.working_dir, item.a_path), "r") as file:
                    after_content = file.read()
                before_content = repo.git.show(f"HEAD:{item.a_path}")
                staged_files.append(
                    {
                        "path": item.a_path,
                        "before": before_content,
                        "after": after_content,
                    }
                )

            return Response(
                {
                    "untracked": untracked_files,
                    "modified": changed_files,
                    "staged": staged_files,
                }
            )

    @action(detail=False, methods=["GET", "POST", "PATCH"])
    def branches(self, request):
        workspace = request.user.current_workspace()
        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_dev_details()
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
                project = Project.objects.create(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                    dbtresource=dbt_details,
                )
                project.create_git_branch()

                return Response(
                    {"branch_name": project.branch_name}, status=status.HTTP_201_CREATED
                )

            elif request.method == "PATCH":
                if not request.data.get("branch_name"):
                    return Response(
                        {"error": "Branch name is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                project = Project.objects.get(
                    dbtresource=dbt_details,
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                )
                with project.repo_context() as (repo, env):
                    name = project.switch_to_git_branch(repo, env)

                return Response({"branch_name": name})

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(detail=False, methods=["GET"])
    def lineage(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        filepath = unquote(request.query_params.get("filepath"))
        predecessor_depth = int(request.query_params.get("predecessor_depth"))
        successor_depth = int(request.query_params.get("successor_depth"))
        lineage_type = request.query_params.get("lineage_type", "all")
        defer = request.query_params.get("defer", True)
        branch_name = request.query_params.get("branch_name")
        if branch_name:
            try:
                project_id = Project.objects.get(
                    workspace=workspace,
                    repository=dbt_details.repository,
                    dbtresource=dbt_details,
                    branch_name=branch_name,
                ).id
            except Project.DoesNotExist:
                return Response(
                    {"error": f"Branch {branch_name} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            project_id = None

        with dbt_details.dbt_transition_context(project_id=project_id) as (
            transition,
            _,
            repo,
        ):
            try:
                transition.mount_manifest(defer=defer)
                transition.mount_catalog(defer=defer)

                node_id = LiveDBTParser.get_node_id_from_filepath(
                    transition.after, filepath, defer
                )
                if not node_id:
                    raise ValueError(
                        f"Node at filepath{filepath} not found in manifest"
                    )

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

                asset_serializer = AssetSerializer(
                    root_asset, context={"request": request}
                )
                lineage_serializer = LineageSerializer(
                    lineage, context={"request": request}
                )
                return Response(
                    {
                        "root_asset": asset_serializer.data,
                        "lineage": lineage_serializer.data,
                    }
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
