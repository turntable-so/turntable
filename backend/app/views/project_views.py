import os
import shlex
import shutil
from urllib.parse import unquote

from django.http import StreamingHttpResponse
from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import AssetSerializer, BranchSerializer, LineageSerializer
from app.core.dbt import LiveDBTParser
from app.models.repository import Branch


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
    def list(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_details()
        if not dbt_details.repository:
            return Response(
                {"error": "No repository found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        branches = BranchSerializer(dbt_details.repository.branches, many=True)

        return Response(branches.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        branch = Branch.objects.get(id=pk)
        branches = BranchSerializer(branch)

        return Response(branches.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def clone(self, request, pk=None):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        branch = Branch.objects.get(id=pk)
        if not branch:
            return Response(
                {"error": "Branch not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(branch.clone(), status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def commit(self, request, pk=None):
        branch = Branch.objects.get(id=pk)
        if not branch.is_cloned:
            return Response(
                {"error": "Branch not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commit_message = request.data.get("commit_message")
        file_paths = request.data.get("file_paths")
        if not commit_message or not file_paths:
            return Response(
                {"error": "Commit message and file paths are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = branch.commit(commit_message, file_paths)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET", "POST", "PUT", "DELETE"])
    def files(self, request, pk=None):
        workspace = request.user.current_workspace()
        user_id = request.user.id

        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_details()
        branch = Branch.objects.get(id=pk)
        if not branch.is_cloned:
            return Response(
                {"error": "Branch not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with branch.repo_context() as (repo, env):
            filepath = request.query_params.get("filepath")
            if filepath and len(filepath) > 0:
                filepath = os.path.join(repo.working_tree_dir, unquote(filepath))
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
                        filepath = os.path.join(
                            repo.working_tree_dir, unquote(filepath)
                        )
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

            root = get_file_tree(user_id, repo.working_tree_dir, repo.working_tree_dir)

        return Response(
            {
                "file_index": [root],
            }
        )

    @action(detail=True, methods=["GET"])
    def changes(self, request, pk=None):
        branch = Branch.objects.get(id=pk)
        if not branch.is_cloned:
            return Response(
                {"error": "Branch not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with branch.repo_context() as (repo, env):
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
        current_user = request.user
        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "GET":
            remote_branches = dbt_details.repository.remote_branches
            main_branch = dbt_details.repository.main_branch.branch_name
            return Response(
                {
                    "main_remote_branch": main_branch,
                    "remote_branches": remote_branches,
                }
            )

        elif request.method == "POST":
            # Implement POST logic here
            if not request.data.get("branch_name"):
                return Response(
                    {"error": "Branch name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.data.get("source_branch"):
                return Response(
                    {"error": "Source branch is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                branch = Branch.objects.create(
                    name=request.data.get("branch_name"),
                    created_by=current_user,
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                )
                branch.create_git_branch(
                    source_branch=request.data.get("source_branch"),
                )

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
