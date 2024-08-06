import os
import tempfile
import zipfile
from contextlib import contextmanager, nullcontext
from io import BytesIO

import yaml
from dotenv import load_dotenv

from app.core.dbt_methods import (
    DBTDialect,
    get_dbt_dialect_from_resource,
    get_dbt_version_from_resource,
)
from app.models import Resource
from vinyl.lib.dbt import DBTProject
from vinyl.lib.dbt_methods import (
    DBTVersion,
)

ARTIFACTS_KEY = "artifacts"
ASSET_GRAPH_JSON_FILE_NAME = "asset_graph.json"
COLUMN_GRAPH_JSON_FILE_NAME = "column_graph.json"

load_dotenv()


@contextmanager
def dbt_repo_context(
    repo_id: str | None = None,
    workspace_id: str | None = None,
    zip_contents: bytes | None = None,
    project_path: str | None = None,
    dialect: DBTDialect | None = None,
    version: DBTVersion | None = None,
    resource: Resource | None = None,
    delete: bool = True,
):
    """
    If repo_id and  are not provided, zip_contents must be provided.
    If resource is not provided, dialect and version must be provided.
    """
    # Assuming 'supabase' is already imported and properly configured
    # and that we have a function get_repo_path(repo_id, ) available

    try:
        if resource is not None and project_path is None:
            project_path = resource.config.get("project_path", None)

        # Downloading the zip contents from Supabase storage
        if zip_contents is None:
            pass
            # repo = Repository.objects.get(id=repo_id)
            # with repo.repo_file.open() as f:
            #     zip_contents = f.read()
        zip_file_like = BytesIO(zip_contents)

        # Creating a temporary directory
        with (
            tempfile.TemporaryDirectory() if delete else nullcontext(tempfile.mkdtemp())
        ) as temp_dir:
            # Extracting contents of the zip file
            with zipfile.ZipFile(zip_file_like, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

                # Getting the path to the project directory
                if project_path is not None:
                    project_path = os.path.join(
                        temp_dir,
                        os.listdir(temp_dir)[0],
                        project_path,
                    )
                else:
                    project_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])

                if dialect is None:
                    if resource is not None:
                        dialect = get_dbt_dialect_from_resource(resource)
                    else:
                        raise ValueError("Must provide dialect or resource")

                if version is None:
                    if resource is not None:
                        version = get_dbt_version_from_resource(resource)
                    else:
                        raise ValueError("Must provide version or resource")

                if resource is not None:
                    env_vars = resource.config.get("env_vars", {})
                    with open(os.path.join(project_path, "dbt_project.yml"), "r") as f:
                        contents = yaml.load(f, Loader=yaml.FullLoader)
                    profile_name = contents["profile"]
                    with (
                        tempfile.TemporaryDirectory()
                        if delete
                        else nullcontext(tempfile.mkdtemp())
                    ) as dbt_profiles_dir:
                        with open(
                            os.path.join(dbt_profiles_dir, "profiles.yml"), "w"
                        ) as f:
                            profile_contents = (
                                dialect.get_dbt_profile_contents_from_resource(resource)
                            )
                            adj_profile_contents = {profile_name: profile_contents}
                            yaml.dump(adj_profile_contents, f)
                            yield (
                                DBTProject(
                                    project_path,
                                    dialect,
                                    version,
                                    dbt_profiles_dir=dbt_profiles_dir,
                                    compile_exclusions=resource.config.get(
                                        "exclusions", None
                                    ),
                                    env_vars=env_vars,
                                ),
                                temp_dir,
                            )
                else:
                    yield DBTProject(project_path, dialect, version), temp_dir

    except Exception as e:
        print("Failed to setup dbt repo context:", str(e))
        raise


def get_repo_path(repo_id, workspace_id):
    return f"{workspace_id}/{repo_id}"


def get_graph_path(repo_id, workspace_id):
    return f"{workspace_id}/{repo_id}"
