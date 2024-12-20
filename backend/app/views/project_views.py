import os
import shutil
import tempfile
import zipfile
from urllib.parse import unquote

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from git import GitCommandError
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import LineageAssetSerializer, LineageSerializer, ProjectSerializer
from app.core.lineage import get_lineage_helper
from app.models.project import Project
from app.views.query_views import format_query


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
        filter_value = request.query_params.get("filter")
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()

        if not dbt_details.repository:
            return Response(
                {"error": "No repository found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get base queryset
        projects = dbt_details.repository.projects

        # Apply filters
        if filter_value:
            if filter_value == "active":
                projects = projects.filter(archived=False)
            elif filter_value == "yours":
                projects = projects.filter(owner=request.user, archived=False)
            elif filter_value == "archived":
                projects = projects.filter(archived=True)

        projects = projects.order_by("-created_at")

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def destroy(self, request, pk=None):
        project = Project.objects.get(id=pk)
        project.archived = True
        project.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
                    if not os.path.exists(filepath):
                        return Response(
                            {"error": "FILE_NOT_FOUND"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    download = (
                        request.query_params.get("download", "false").lower() == "true"
                    )
                    if download:
                        if os.path.isfile(filepath):
                            with open(filepath, "rb") as file:
                                response = HttpResponse(
                                    file.read(), content_type="application/octet-stream"
                                )
                                response["Content-Disposition"] = (
                                    f'attachment; filename="{os.path.basename(filepath)}"'
                                )
                                return response
                        elif os.path.isdir(filepath):
                            with tempfile.NamedTemporaryFile(
                                suffix=".zip", delete=False
                            ) as temp_zip_file:
                                temp_zip_path = temp_zip_file.name
                                with zipfile.ZipFile(
                                    temp_zip_file, "w", zipfile.ZIP_DEFLATED
                                ) as zipf:
                                    base_path = os.path.dirname(filepath)
                                    for root, _, files in os.walk(filepath):
                                        for file in files:
                                            file_path = os.path.join(root, file)
                                            arcname = os.path.relpath(
                                                file_path, base_path
                                            )
                                            zipf.write(file_path, arcname)

                            with open(temp_zip_path, "rb") as f:
                                response = HttpResponse(
                                    f.read(), content_type="application/zip"
                                )
                                response["Content-Disposition"] = (
                                    f'attachment; filename="{os.path.basename(filepath)}.zip"'
                                )
                            os.remove(temp_zip_path)
                            return response
                        else:
                            return Response(
                                {"error": "Path is neither a file nor a directory"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    file_size = os.path.getsize(filepath)
                    FILE_SIZE_LIMIT = 1024 * 1024  # 1MB
                    if file_size > FILE_SIZE_LIMIT:
                        return Response(
                            {"error": "FILE_EXCEEDS_SIZE_LIMIT"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
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

    @action(detail=True, methods=["POST"], url_path="files/duplicate")
    def duplicate(self, request, pk=None):
        filepath = request.data.get("filepath")
        if not filepath:
            return Response(
                {"success": False, "error": "filepath is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = Project.objects.get(id=pk)
        try:
            with project.repo_context() as (repo, env):
                filepath = os.path.join(repo.working_tree_dir, unquote(filepath))
                if not os.path.exists(filepath):
                    return Response(
                        {"success": False, "error": "File or directory not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                base_dir = os.path.dirname(filepath)
                base_name = os.path.basename(filepath)
                name, ext = os.path.splitext(base_name)

                if os.path.isfile(filepath):
                    new_name = f"{name} copy{ext}"
                    new_path = os.path.join(base_dir, new_name)
                    shutil.copy2(filepath, new_path)
                else:
                    new_name = f"{base_name} copy"
                    new_path = os.path.join(base_dir, new_name)
                    shutil.copytree(filepath, new_path)

            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["PUT"], url_path="files/move")
    def move(self, request, pk=None):
        drag_ids = request.data.get("drag_ids")
        parent_id = request.data.get("parent_id")

        if not drag_ids or not parent_id:
            return Response(
                {
                    "success": False,
                    "error": "drag_ids and parent_id are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = Project.objects.get(id=pk)
        try:
            with project.repo_context() as (repo, env):
                # Convert paths to absolute paths within repo
                parent_path = os.path.join(repo.working_tree_dir, unquote(parent_id))
                if not os.path.exists(parent_path):
                    return Response(
                        {"success": False, "error": "Parent directory not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Move each dragged item
                for drag_id in drag_ids:
                    source_path = os.path.join(repo.working_tree_dir, unquote(drag_id))
                    if not os.path.exists(source_path):
                        return Response(
                            {
                                "success": False,
                                "error": f"Source path not found: {drag_id}",
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    # Create destination path
                    filename = os.path.basename(source_path)
                    dest_path = os.path.join(parent_path, filename)

                    # Handle case where destination already exists
                    if os.path.exists(dest_path):
                        return Response(
                            {
                                "success": False,
                                "error": f"Destination already exists: {filename}",
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                    # Move the file/directory
                    shutil.move(source_path, dest_path)

                return Response({"success": True}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

    @action(detail=True, methods=["POST"])
    def sync(self, request, pk=None):
        project = Project.objects.get(id=pk)
        if not project.is_cloned:
            return Response(
                {"error": "Project not cloned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with project.repo_context() as (repo, _):
            with project.repository.with_ssh_env() as env:
                if repo.is_dirty(untracked_files=True):
                    return Response(
                        {
                            "error": "UNCOMMITTED_CHANGES",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                with repo.config_writer() as git_config:
                    # Configure the user name and email
                    # github doesn't actually use this, but it's required by git
                    git_config.set_value("user", "name", "NAME")
                    # github uses the email for commit authorship
                    git_config.set_value("user", "email", request.user.email)

                    try:
                        base_branch = project.source_branch or "main"
                        repo.git.fetch("origin", base_branch, env=env)
                        repo.git.merge(f"origin/{base_branch}", env=env)

                        return Response(
                            {"detail": "success"},
                            status=status.HTTP_200_OK,
                        )
                    except GitCommandError as e:
                        error_string = str(e).lower()
                        if "merge_head exists" in error_string:
                            try:
                                repo.git.merge("--abort", env=env)
                            except GitCommandError:
                                pass
                            return Response(
                                {"error": "MERGE_HEAD_EXISTS"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        elif "merge conflict" in error_string:
                            try:
                                repo.git.merge("--abort", env=env)
                            except GitCommandError:
                                pass
                            return Response(
                                {"error": "MERGE_CONFLICT"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        else:
                            return Response(
                                {"error": "INTERNAL_SERVER_ERROR"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )
                    finally:
                        git_config.set_value("user", "name", "")
                        git_config.set_value("user", "email", "")

    def create(self, request):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()
        if not dbt_details:
            return Response(
                {"error": "No DBT details found for this workspace"},
                status=status.HTTP_404_NOT_FOUND,
            )

        branch_name = request.data.get("branch_name")
        source_branch = request.data.get("source_branch")
        schema = request.data.get("schema")

        if not branch_name:
            return Response(
                {"error": "Branch name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not source_branch:
            return Response(
                {"error": "Source branch is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not schema:
            return Response(
                {"error": "Schema is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if a project with the same name exists and is not archived
        existing_project = Project.objects.filter(
            name=branch_name, workspace=workspace, archived=False
        ).first()
        if existing_project:
            return Response(
                {"error": "A project with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the branch already exists in the repository
        repo = dbt_details.repository
        remote_branches = repo.remote_branches
        if branch_name in remote_branches:
            return Response(
                {"error": "A branch with this name already exists in the repository"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            project = Project.objects.create(
                name=request.data.get("branch_name"),
                workspace=workspace,
                repository=dbt_details.repository,
                branch_name=request.data.get("branch_name"),
                schema=request.data.get("schema"),
                source_branch=request.data.get("source_branch"),
                owner=request.user,
            )
            project.create_git_branch(
                source_branch=request.data.get("source_branch"),
            )

        project_serializer = ProjectSerializer(project)
        return Response(project_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET", "POST", "PATCH"])
    def branches(self, request):
        workspace = request.user.current_workspace()
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
            # Redirect to create method
            return self.create(request)

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    class ProjectLineageSerializer(serializers.Serializer):
        asset_only = serializers.BooleanField(required=False, default=False)
        filepath = serializers.CharField(required=True)
        predecessor_depth = serializers.IntegerField(required=True)
        successor_depth = serializers.IntegerField(required=True)
        lineage_type = serializers.ChoiceField(
            choices=["all", "direct_only"], required=False, default="all"
        )

    @action(detail=True, methods=["GET"])
    def lineage(self, request, pk=None):
        workspace = request.user.current_workspace()
        dbt_details = workspace.get_dbt_dev_details()

        project = Project.objects.get(id=pk)

        serializer = self.ProjectLineageSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        asset_only = bool(serializer.validated_data.get("asset_only"))
        filepath = unquote(serializer.validated_data.get("filepath"))
        predecessor_depth = serializer.validated_data.get("predecessor_depth")
        successor_depth = serializer.validated_data.get("successor_depth")
        lineage_type = serializer.validated_data.get("lineage_type")

        with dbt_details.dbt_repo_context(project_id=project.id, isolate=False) as (
            proj,
            _,
            _,
        ):
            try:
                root_asset, lineage = get_lineage_helper(
                    proj=proj,
                    before_proj=None,
                    resource=dbt_details.resource,
                    filepath=filepath,
                    predecessor_depth=predecessor_depth,
                    successor_depth=successor_depth,
                    lineage_type=lineage_type,
                    defer=False,
                    asset_only=asset_only,
                )
            except KeyError as e:
                return Response(
                    {"error": f"Node {str(e)} does not exist in graph"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        asset_serializer = LineageAssetSerializer(
            root_asset, context={"request": request}
        )
        lineage_serializer = LineageSerializer(
            lineage,
            context={"request": request},
        )
        return Response(
            {
                "root_asset": asset_serializer.data,
                "lineage": lineage_serializer.data,
            }
        )

    class CompileQueryPayloadSerializer(serializers.Serializer):
        filepath = serializers.CharField(required=True)

        def validate_filepath(self, value):
            return unquote(value)

    @action(detail=True, methods=["POST"])
    def compile(self, request, pk=None):
        project = Project.objects.get(id=pk)
        workspace = request.user.current_workspace()
        dbt_resource = workspace.get_dbt_dev_details()

        serializer = self.CompileQueryPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filepath = serializer.validated_data.get("filepath")

        with dbt_resource.dbt_repo_context(project_id=project.id, isolate=False) as (
            project,
            project_path,
            _,
        ):
            project_filepath = os.path.join(project_path, filepath)
            if not os.path.exists(project_filepath):
                return Response(
                    {"error": "File not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            with open(project_filepath, "r") as file:
                dbt_sql = file.read()

            try:
                sql = project.fast_compile(dbt_sql)
                if not sql:
                    sql = project.preview(dbt_sql, data=False)

            except Exception as e:
                ## TODO: this is hacky, we'll eventually want a more robust error handling solution
                if "Compilation Error" in str(e):
                    error_message = str(e).split("Compilation Error")[1].strip()
                    return Response(
                        {"error": error_message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    raise e

            return Response(sql, status=status.HTTP_200_OK)
