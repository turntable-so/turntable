import os
import shutil
from urllib.parse import unquote

from django.db import transaction
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import AssetSerializer, LineageSerializer, ProjectSerializer
from app.core.dbt import LiveDBTParser
from app.models.project import Project
from app.models.resources import Resource
from app.views.query_views import format_query
from vinyl.lib.dbt import DBTProject, DBTTransition


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


def get_lineage_helper(
    proj: DBTProject,
    before_proj: DBTProject | None,
    resource: Resource,
    filepath: str,
    predecessor_depth: int,
    successor_depth: int,
    lineage_type: str,
    defer: bool,
):
    if defer:
        transition = DBTTransition(before_project=before_proj, after_project=proj)
        transition.mount_manifest(defer=defer)
        transition.mount_catalog(defer=defer)
    else:
        proj.mount_manifest()
        proj.mount_catalog()

    node_id = LiveDBTParser.get_node_id_from_filepath(proj, filepath, defer)
    if not node_id:
        raise ValueError(f"Node at filepath{filepath} not found in manifest")

    dbtparser = LiveDBTParser.parse_project(
        proj=proj,
        before_proj=before_proj,
        node_id=node_id,
        resource=resource,
        predecessor_depth=predecessor_depth,
        successor_depth=successor_depth,
        defer=defer,
    )
    lineage, _ = dbtparser.get_lineage(lineage_type=lineage_type)
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

    return root_asset, lineage

    asset_serializer = AssetSerializer(root_asset, context={"request": request})
    lineage_serializer = LineageSerializer(lineage, context={"request": request})
    return Response(
        {
            "root_asset": asset_serializer.data,
            "lineage": lineage_serializer.data,
        }
    )


class ProjectViewSet(viewsets.ViewSet):
    def list(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        if not dbt_details.repository:
            return Response(
                {"error": "No repository found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        projects = ProjectSerializer(dbt_details.repository.projects, many=True)

        return Response(projects.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        project = Project.objects.get(id=pk)
        projects = ProjectSerializer(project)

        return Response(projects.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def clone(self, request, pk=None):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        project = Project.objects.get(id=pk)
        if not project:
            return Response(
                {"error": "Project not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(project.clone(), status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def discard(self, request, pk=None):
        project = Project.objects.get(id=pk)
        if not project.is_cloned:
            return Response(
                {"error": "Project not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.discard_changes()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def commit(self, request, pk=None):
        project = Project.objects.get(id=pk)
        if not project.is_cloned:
            return Response(
                {"error": "Project not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commit_message = request.data.get("commit_message")
        file_paths = request.data.get("file_paths")
        if not commit_message or not file_paths:
            return Response(
                {"error": "Commit message and file paths are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = project.commit(
            commit_message=commit_message,
            file_paths=file_paths,
            user_email=request.user.email,
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    def files(self, request, pk=None):
        workspace = request.user.current_workspace()
        user_id = request.user.id

        # assumes a single repo in the workspace for now
        dbt_details = workspace.get_dbt_dev_details()
        project = Project.objects.get(id=pk)

        with project.repo_context() as (repo, env):
            filepath = request.query_params.get("filepath")
            if filepath and len(filepath) > 0:
                filepath = os.path.join(repo.working_tree_dir, unquote(filepath))
                if request.method == "POST":
                    if os.path.exists(filepath):
                        return Response(
                            {"error": "file already exists"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    if request.data.get("is_directory"):
                        os.makedirs(filepath, exist_ok=True)
                        return Response(status=status.HTTP_201_CREATED)

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
                    format = request.data.get("format")
                    contents = request.data.get("contents")
                    if format and filepath.endswith(".sql"):
                        contents = format_query(contents)

                    with open(filepath, "w") as file:
                        file.write(contents)
                    return JsonResponse({"content": contents})

                if request.method == "PATCH":
                    new_path = request.data.get("new_path")
                    if not new_path:
                        return Response(
                            {"error": "New path is required"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    new_path = os.path.join(repo.working_tree_dir, unquote(new_path))
                    if os.path.isdir(filepath):
                        shutil.move(filepath, new_path)
                    else:
                        os.rename(filepath, new_path)
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
        project = Project.objects.get(id=pk)
        if not project.is_cloned:
            return Response(
                {"error": "Project not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with project.repo_context() as (repo, env):
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
            deleted_files = []
            for item in repo.index.diff(None):
                file_data = {
                    "path": item.a_path,
                    "before": "",
                    "after": "",
                }
                # Handle deleted files
                if item.deleted_file:
                    file_data["before"] = repo.git.show(f"HEAD:{item.a_path}")
                    file_data["after"] = ""
                    deleted_files.append(file_data)
                # Handle renamed files
                else:
                    file_data["before"] = repo.git.show(f"HEAD:{item.a_path}")
                    with open(os.path.join(repo.working_dir, item.a_path), "r") as file:
                        file_data["after"] = file.read()
                        changed_files.append(file_data)

            return Response(
                {
                    "untracked": untracked_files,
                    "modified": changed_files,
                    "deleted": deleted_files,
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

        if request.method == "GET":
            remote_branches = dbt_details.repository.remote_branches
            main_branch = dbt_details.repository.main_project.branch_name
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
            if not request.data.get("schema"):
                return Response(
                    {"error": "Schema is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                project = Project.objects.create(
                    name=request.data.get("branch_name"),
                    workspace=workspace,
                    repository=dbt_details.repository,
                    branch_name=request.data.get("branch_name"),
                    schema=request.data.get("schema"),
                )
                project.create_git_branch(
                    source_branch=request.data.get("source_branch"),
                )

            project_serializer = ProjectSerializer(project)
            return Response(project_serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "PATCH":
            if not request.data.get("branch_name"):
                return Response(
                    {"error": "Branch name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            project = Project.objects.get(
                workspace=workspace,
                repository=dbt_details.repository,
                branch_name=request.data.get("branch_name"),
            )
            with project.repo_context() as (repo, env):
                name = project.switch_to_git_branch(repo, env)

            return Response({"branch_name": name})

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(detail=True, methods=["GET"])
    def lineage(self, request, pk=None):
        workspace = request.user.current_workspace()
        project = Project.objects.get(id=pk)

        dbt_details = workspace.get_dbt_dev_details()
        filepath = unquote(request.query_params.get("filepath"))
        predecessor_depth = int(request.query_params.get("predecessor_depth"))
        successor_depth = int(request.query_params.get("successor_depth"))
        lineage_type = request.query_params.get("lineage_type", "all")
        defer = request.query_params.get("defer", False)
        if lineage_type not in ["all", "direct_only"]:
            return Response(
                {
                    "error": "lineage_type query parameter must be either 'all' or 'direct_only'."
                },
                status=400,
            )

        if defer:
            with dbt_details.dbt_transition_context(
                project_id=project.id, isolate=False
            ) as (
                transition,
                _,
                repo,
            ):
                root_asset, lineage = get_lineage_helper(
                    proj=transition.after,
                    before_proj=transition.before,
                    resource=dbt_details.resource,
                    filepath=filepath,
                    predecessor_depth=predecessor_depth,
                    successor_depth=successor_depth,
                    lineage_type=lineage_type,
                    defer=defer,
                )
        else:
            with dbt_details.dbt_repo_context(project_id=project.id, isolate=False) as (
                proj,
                _,
                _,
            ):
                root_asset, lineage = get_lineage_helper(
                    proj=proj,
                    before_proj=None,
                    resource=dbt_details.resource,
                    filepath=filepath,
                    predecessor_depth=predecessor_depth,
                    successor_depth=successor_depth,
                    lineage_type=lineage_type,
                    defer=defer,
                )

        asset_serializer = AssetSerializer(root_asset, context={"request": request})
        lineage_serializer = LineageSerializer(lineage, context={"request": request})
        return Response(
            {
                "root_asset": asset_serializer.data,
                "lineage": lineage_serializer.data,
            }
        )
