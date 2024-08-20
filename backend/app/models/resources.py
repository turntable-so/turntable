import json
import os
import re
import tempfile
import uuid
from contextlib import contextmanager
from typing import Any

import yaml
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import models
from polymorphic.models import PolymorphicModel

from app.models.auth import Workspace
from app.models.git_connections import GithubInstallation
from app.services.code_repo_service import CodeRepoService
from app.services.github_service import GithubService
from app.utils.fields import encrypt
from vinyl.lib.connect import (
    BigQueryConnector,
    DatabaseFileConnector,
    PostgresConnector,
)
from vinyl.lib.dbt import DBTProject
from vinyl.lib.dbt_methods import DBTDialect, DBTVersion
from vinyl.lib.utils.files import save_orjson
from vinyl.lib.utils.process import run_and_capture_subprocess


class WorkflowStatus(models.TextChoices):
    RUNNING = "RUNNING", "Running"
    FAILED = "FAILED", "Failed"
    SUCCESS = "SUCCESS", "Success"


# Helper classes
class ResourceType(models.TextChoices):
    DB = "db", "Database"
    BI = "bi", "BI Tool"


class ResourceSubtype(models.TextChoices):
    LOOKER = "looker", "Looker"
    METABASE = "metabase", "Metabase"
    BIGQUERY = "bigquery", "BigQuery"
    SNOWFLAKE = "snowflake", "Snowflake"
    POSTGRES = "postgres", "Postgres"
    DUCKDB = "duckdb", "File"
    FILE = "file", "File"
    DBT = "dbt", "Dbt"
    DBT_CLOUD = "dbt_cloud", "Dbt Cloud"


# helper functions
def get_sync_config(db_path):
    return {
        "type": "datahub-lite",
        "config": {
            "type": "duckdb",
            "config": {"file": db_path},
        },
    }


@contextmanager
def repo_path(obj):
    github_repo_id = getattr(obj, "github_repo_id")
    github_installation_id = getattr(obj, "github_installation_id")
    project_path = getattr(obj, "project_path")
    git_repo_url = getattr(obj, "git_repo_url")
    if git_repo_url is not None:
        deploy_key = getattr(obj, "deploy_key")
        coderepo_service = CodeRepoService(obj.resource.workspace.id)
        with coderepo_service.repo_context(
            public_key=deploy_key,
            git_repo_url=git_repo_url,
        ) as temp_dir:
            project_path = os.path.join(temp_dir, project_path)

            yield project_path
    elif github_repo_id is not None and github_installation_id is not None:
        github_service = GithubService(
            obj.resource.workspace.id, github_installation_id
        )
        repo = github_service.get_repository_by_id(github_repo_id)
        with github_service.repo_context(repo.id) as (zip_contents, temp_dir):
            project_path = os.path.join(temp_dir, os.listdir(temp_dir)[0], project_path)
            yield project_path
    else:
        yield project_path


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    name = models.TextField(null=True)
    type = models.TextField(choices=ResourceType.choices, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    creator = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, default=None
    )
    datahub_db = models.FileField(upload_to="datahub_dbs/", null=True)

    class Meta:
        indexes = [
            models.Index(fields=["workspace_id"]),
        ]

    def _get_latest_sync_run(self):
        try:
            workflow_run = self.workflow_runs.order_by("-created_at").first()
            return workflow_run
        except ObjectDoesNotExist:
            return None

    @property
    def status(self):
        run = self._get_latest_sync_run()
        return run.status if run else None

    @property
    def last_synced(self):
        run = self._get_latest_sync_run()
        return run.updated_at if run else None

    @property
    def subtype(self):
        return self.details.subtype

    @property
    def has_dbt(self):
        return self.dbtresource_set.exists()


class ResourceDetails(PolymorphicModel):
    name = models.CharField(max_length=255, blank=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    resource = models.OneToOneField(
        Resource, on_delete=models.CASCADE, null=True, related_name="details"
    )

    class Meta:
        indexes = [
            models.Index(fields=["resource_id"]),
        ]

    @property
    def venv_path(self):
        pass

    @property
    def datahub_extras(self) -> list[str]:
        pass

    @property
    def datahub_db_nickname(self) -> str:
        return self.datahub_extras[0] if self.datahub_extras else "datahub"

    @property
    def test_number_of_entries(self) -> int:
        return 3

    def get_venv_python(self):
        # only works on unix
        return f"{os.path.abspath(self.venv_path)}/bin/python"

    def activate_datahub_env(self):
        run_and_capture_subprocess(
            f". {self.venv_path}/bin/activate", shell=True, check=True
        )

    def create_venv_and_install_datahub(self):
        if os.path.exists(self.venv_path):
            self.activate_datahub_env()
            return

        # Create a virtual environment
        run_and_capture_subprocess(["uv", "venv", self.venv_path], check=True)

        # activate the virtual environment
        self.activate_datahub_env()

        # Install datahub with correct extras
        run_and_capture_subprocess(
            [
                "uv",
                "pip",
                "install",
                "acryl-datahub[datahub-lite]",
                *[f"acryl-datahub[{extra}]" for extra in self.datahub_extras],
                "--python",
                self.get_venv_python(),
            ],
            check=True,
        )

    def run_datahub_ingest(self):
        self.create_venv_and_install_datahub()

        # run ingest
        with self.datahub_yaml_path() as (config_paths, db_path):
            for path in config_paths:
                run_and_capture_subprocess(
                    [
                        self.get_venv_python(),
                        "-m",
                        "datahub",
                        "ingest",
                        "-c",
                        path,
                    ],
                )
            with open(db_path, "rb") as f:
                self.resource.datahub_db.save(
                    os.path.basename(db_path), File(f), save=True
                )

    def test_datahub_connection(self):
        self.create_venv_and_install_datahub()

        # run ingest test
        log_pattern = re.compile(
            r"(?P<datetime>.+?)\s+(?P<level>\w+)\s+(?P<message>.+)"
        )
        errors = []
        with self.datahub_yaml_path() as (config_paths, db_path):
            for path in config_paths:
                if os.path.basename(path) == "dbt.yml":
                    # skip dbt config
                    continue
                with tempfile.NamedTemporaryFile(suffix=".log", mode="r+") as log_file:
                    run_and_capture_subprocess(
                        [
                            self.get_venv_python(),
                            "-m",
                            "datahub",
                            "--log-file",
                            log_file.name,
                            "ingest",
                            "-c",
                            path,
                            "--preview",
                            "--preview-workunits",
                            str(self.test_number_of_entries),
                        ]
                    )
                    log_contents = log_file.read()
                for line in log_contents.splitlines():
                    match = log_pattern.match(line)
                    if match and match.group("level") == "ERROR":
                        errors.append(
                            {
                                "connection_type": os.path.basename(path).split(".")[0],
                                "error_message": match.group("message"),
                            }
                        )
            if len(errors) > 0:
                return {"success": False, "errors": errors}
            return {"success": True}

    def get_datahub_config(self, db_path) -> dict[str, Any]:
        pass

    def add_detail(self, detail):
        detail.resource = self.resource
        detail.save()

    @contextmanager
    def datahub_yaml_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, self.datahub_db_nickname + ".duckdb")
            config_path = os.path.join(temp_dir, self.datahub_db_nickname + ".yml")
            # add in dbt configs to same ingest
            config = self.get_datahub_config(db_path)
            with open(config_path, "w") as f:
                yaml.dump(config, f)
            yield [config_path], db_path


class DBTResource(PolymorphicModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True)
    name = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    creator = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, default=None
    )
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True)
    manifest_json = models.JSONField(null=True)
    catalog_json = models.JSONField(null=True)

    @classmethod
    def get_default_subtype(cls):
        return ResourceSubtype.DBT


## BI polymorphisms
class LookerDetails(ResourceDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.LOOKER)
    base_url = encrypt(models.URLField(blank=False))
    client_id = encrypt(models.CharField(max_length=255, blank=False))
    client_secret = encrypt(models.CharField(max_length=255, blank=False))
    github_repo_id = encrypt(models.CharField(max_length=255, null=True))
    project_path = models.CharField(max_length=255, null=True)
    github_installation = models.ForeignKey(
        GithubInstallation, null=True, on_delete=models.CASCADE
    )

    @property
    def venv_path(self):
        return ".lookervenv"

    @property
    def datahub_extras(self):
        return ["looker", "lookml"]

    @property
    def datahub_db_nickname(self):
        return "looker"

    def get_datahub_config(self, db_path) -> dict[str, Any]:
        return {
            "source": {
                "type": "looker",
                "config": {
                    "base_url": self.base_url,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            },
            "sink": get_sync_config(db_path),
        }

    # special config function for lookml. Looker uses two separate processing steps
    def get_datahub_config_lookml(self, db_path, project_path) -> dict[str, Any]:
        return {
            "source": {
                "type": "lookml",
                "config": {
                    "base_folder": project_path,
                    "api": {
                        "base_url": self.base_url,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                },
            },
            "sink": get_sync_config(db_path),
        }

    @contextmanager
    def datahub_yaml_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, self.datahub_db_nickname + ".duckdb")
            config_path = os.path.join(temp_dir, self.datahub_db_nickname + ".yml")
            config = self.get_datahub_config(db_path)
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            if self.project_path is None:
                yield [config_path], db_path

            else:
                # add in lookml configs, may need to use github
                with repo_path(self) as project_path:
                    config_path_lookml = os.path.join(temp_dir, "lookml.yml")
                    config_lookml = self.get_datahub_config_lookml(
                        db_path, project_path
                    )
                    with open(config_path_lookml, "w") as f:
                        yaml.dump(config_lookml, f)

                    yield [config_path, config_path_lookml], db_path


class MetabaseDetails(ResourceDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.METABASE)
    username = encrypt(models.CharField(max_length=255, blank=False))
    password = encrypt(models.CharField(max_length=255, blank=False))
    connect_uri = encrypt(models.URLField(blank=False))

    @property
    def venv_path(self):
        return ".metabasevenv"

    @property
    def datahub_extras(self):
        return ["metabase"]

    @contextmanager
    def datahub_yaml_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, self.datahub_extras[0] + ".duckdb")
            config_path = os.path.join(temp_dir, self.datahub_extras[0] + ".yml")
            config = {
                "source": {
                    "type": "metabase",
                    "config": {
                        "connect_uri": self.connect_uri,
                        "username": self.username,
                        "password": self.password,
                    },
                },
                "sink": get_sync_config(db_path),
            }
            with open(config_path, "w") as f:
                yaml.dump(config, f)
            yield [config_path], db_path


## DBT polymorphisms
class DBTCoreDetails(DBTResource):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.DBT)
    github_installation = models.ForeignKey(
        GithubInstallation, null=True, on_delete=models.CASCADE
    )
    github_repo_id = encrypt(models.CharField(max_length=255, null=True))
    deploy_key = encrypt(models.TextField(null=True))
    git_repo_url = models.CharField(max_length=255, null=True)
    main_git_branch = models.CharField(max_length=255, null=True)
    project_path = models.CharField(max_length=255, blank=False)
    database = encrypt(models.CharField(max_length=255, blank=False))
    schema = encrypt(models.CharField(max_length=255, blank=False))
    other_schemas = encrypt(ArrayField(models.CharField(max_length=255), null=True))
    threads = models.IntegerField(null=True, default=1)
    version = models.CharField(
        choices=[(v, v.value) for v in DBTVersion], max_length=255, blank=False
    )
    env_vars = encrypt(models.JSONField(null=True))

    @contextmanager
    def dbt_repo_context(self):
        env_vars = self.env_vars or {}
        dialect_str = self.resource.details.subtype
        with repo_path(self) as project_path:
            with open(os.path.join(project_path, "dbt_project.yml"), "r") as f:
                contents = yaml.load(f, Loader=yaml.FullLoader)
            profile_name = contents["profile"]
            with tempfile.TemporaryDirectory() as dbt_profiles_dir:
                with open(os.path.join(dbt_profiles_dir, "profiles.yml"), "w") as f:
                    profile_contents = self.resource.details.get_dbt_profile_contents(
                        self
                    )
                    adj_profile_contents = {profile_name: profile_contents}
                    yaml.dump(adj_profile_contents, f)
                with open(os.path.join(dbt_profiles_dir, "profiles.yml"), "r") as f:
                    yield (
                        DBTProject(
                            project_path,
                            DBTDialect._value2member_map_[dialect_str],
                            self.version,
                            dbt_profiles_dir=dbt_profiles_dir,
                            env_vars={} if env_vars is None else env_vars,
                        ),
                        project_path,
                    )

    def upload_artifacts(self):
        with self.dbt_repo_context() as (dbtproj, project_path):
            stdout, stderr, success = dbtproj.dbt_compile(
                models_only=True, update_manifest=True
            )
            if not success:
                raise Exception(
                    f"Error compiling dbt code. Stderr: {stderr}. Stdout: {stdout}"
                )
            stdout, stderr, success = dbtproj.dbt_docs_generate()
            if not success:
                raise Exception(
                    f"Error generating docs. Stderr: {stderr}. Stdout: {stdout}"
                )
            dbtproj.mount_manifest()
            dbtproj.mount_catalog()
            self.manifest_json = dbtproj.manifest
            self.catalog_json = dbtproj.catalog
            self.save()

    @contextmanager
    def datahub_yaml_path(self, db_path):
        with tempfile.TemporaryDirectory() as artifact_dir:
            manifest_path = os.path.join(artifact_dir, "manifest.json")
            catalog_path = os.path.join(artifact_dir, "catalog.json")
            save_orjson(manifest_path, self.manifest_json)
            save_orjson(catalog_path, self.catalog_json)
            with tempfile.TemporaryDirectory() as temp_dir:
                config_path = os.path.join(temp_dir, "dbt.yml")
                config = {
                    "source": {
                        "type": "dbt",
                        "config": {
                            "manifest_path": manifest_path,
                            "catalog_path": catalog_path,
                            "target_platform": self.resource.details.subtype,
                            "write_semantics": "override",
                            "include_column_lineage": False,
                        },
                    },
                    "sink": get_sync_config(db_path),
                }
                with open(config_path, "w") as f:
                    yaml.dump(config, f)
                yield [config_path]


class DBTCloudDetails(DBTResource):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.DBT_CLOUD)
    api_token = encrypt(models.CharField(max_length=255, blank=False))
    account_id = encrypt(models.CharField(max_length=255, blank=False))
    project_id = encrypt(models.CharField(max_length=255, blank=False))


## DB polymorphisms
class DBDetails(ResourceDetails):
    lookback_days = models.IntegerField(default=1)
    database_include = ArrayField(models.CharField(max_length=255), null=True)
    database_exclude = ArrayField(models.CharField(max_length=255), null=True)
    schema_include = ArrayField(models.CharField(max_length=255), null=True)
    schema_exclude = ArrayField(models.CharField(max_length=255), null=True)
    table_include = ArrayField(models.CharField(max_length=255), null=True)
    table_exclude = ArrayField(models.CharField(max_length=255), null=True)
    use_only_dbt_schemas = models.BooleanField(default=False)

    @property
    def requires_start_date(self):
        return True

    @property
    def allows_db_exclusions(self):
        return False

    def get_dbt_profile_contents(self, dbt_core_resource: DBTCoreDetails):
        pass

    @contextmanager
    def dbt_datahub_yml_paths(self, dbtresources: list[DBTResource], db_path):
        if len(dbtresources) == 0:
            yield []
            return

        with dbtresources[0].datahub_yaml_path(db_path) as config_paths:
            with self.dbt_datahub_yml_paths(
                dbtresources[1:], db_path
            ) as other_config_paths:
                yield config_paths + other_config_paths

    def add_patterns_to_datahub_config(self, config):
        config_subset = config["source"]["config"]
        if self.allows_db_exclusions:
            if self.database_include is not None:
                config_subset.setdefault("schema_pattern", {}).setdefault(
                    "allow", self.database_include
                )
            if self.database_exclude is not None:
                config_subset.setdefault("schema_pattern", {}).setdefault(
                    "deny", self.database_exclude
                )

        if self.schema_include is not None or self.use_only_dbt_schemas:
            config_subset.setdefault("schema_pattern", {}).setdefault(
                "allow", self.schema_include or []
            )
        if self.schema_exclude is not None:
            config_subset.setdefault("schema_pattern", {}).setdefault(
                "deny", self.schema_exclude
            )
        if self.table_include is not None:
            config_subset.setdefault("table_pattern", {}).setdefault(
                "allow", self.table_include
            )
        if self.table_exclude is not None:
            config_subset.setdefault("table_pattern", {}).setdefault(
                "deny", self.table_exclude
            )

    @contextmanager
    def datahub_yaml_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, self.datahub_db_nickname + ".duckdb")
            config_path = os.path.join(temp_dir, self.datahub_db_nickname + ".yml")
            # add in dbt configs to same ingest, only supports dbt core for now
            dbt_resources: list[DBTCoreDetails] = list(
                self.resource.dbtresource_set.all()
            )
            with self.dbt_datahub_yml_paths(dbt_resources, db_path) as dbt_yaml_paths:
                config = self.get_datahub_config(db_path)
                self.add_patterns_to_datahub_config(config)
                schema_pattern = config["source"]["config"].get("schema_pattern", {})
                allow_list = schema_pattern.get("allow")
                # add dbt schemas to allow list if not pulling from all schemas
                if allow_list is not None:
                    for dbt in dbt_resources:
                        schema_pattern["allow"].append(dbt.schema)
                        if dbt.other_schemas is not None:
                            schema_pattern["allow"].extend(dbt.other_schemas)
                with open(config_path, "w") as f:
                    yaml.dump(config, f)
                yield [config_path, *dbt_yaml_paths], db_path


class PostgresDetails(DBDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.POSTGRES)
    host = encrypt(models.CharField(max_length=255, blank=False))
    port = models.IntegerField(blank=False)
    database = encrypt(models.CharField(max_length=255, blank=False))
    username = encrypt(models.CharField(max_length=255, blank=False))
    password = encrypt(models.CharField(max_length=255, blank=False))

    @property
    def requires_start_date(self):
        return False

    @property
    def venv_path(self):
        return ".postgresvenv"

    @property
    def datahub_extras(self):
        return ["postgres", "dbt"]

    def get_connector(self):
        return PostgresConnector(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            tables=[f"{self.database}.*.*"],
        )

    def get_datahub_config(self, db_path) -> dict[str, Any]:
        return {
            "source": {
                "type": "postgres",
                "config": {
                    "host_port": f"{self.host}:{self.port}",
                    "database": self.database,
                    "username": self.username,
                    "password": self.password,
                },
            },
            "sink": get_sync_config(db_path),
        }

    def get_dbt_profile_contents(self, dbt_core_resource: DBTCoreDetails):
        if dbt_core_resource.database != self.database:
            raise Exception(
                f"DBT database {dbt_core_resource.database} does not match Postgres database {self.database}"
            )
        return {
            "target": "prod",
            "outputs": {
                "prod": {
                    "type": "postgres",
                    "host": self.host,
                    "port": self.port,
                    "dbname": self.database,
                    "schema": dbt_core_resource.schema,
                    "user": self.username,
                    "password": self.password,
                }
            },
        }


class BigqueryDetails(DBDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.BIGQUERY)
    service_account = encrypt(models.JSONField())

    @property
    def venv_path(self):
        return ".bigqueryvenv"

    @property
    def datahub_extras(self):
        return ["bigquery", "dbt"]

    def get_connector(self):
        return BigQueryConnector(
            service_account_info=self.service_account,
            tables=[f"{self.service_account['project']}.*.*"],
        )

    def get_datahub_config(self, db_path):
        adj_service_account = json.loads(self.service_account)
        adj_service_account.pop("universe_domain", None)
        return {
            "source": {
                "type": "bigquery",
                "config": {
                    "start_time": f"-{self.lookback_days}d",
                    "credential": adj_service_account,
                    "project_ids": [adj_service_account["project_id"]],
                    "include_table_lineage": False,
                    "include_table_location_lineage": False,
                    "include_view_lineage": False,
                    "include_view_column_lineage": False,
                    "include_table_snapshots": False,
                    "include_usage_statistics": False,
                },
            },
            "sink": get_sync_config(db_path),
        }

    def get_dbt_profile_contents(self, dbt_core_resource: DBTCoreDetails):
        return {
            "target": "prod",
            "outputs": {
                "prod": {
                    "type": "bigquery",
                    "method": "service-account-json",
                    "project": dbt_core_resource.database,
                    "schema": dbt_core_resource.schema,
                    "keyfile_json": self.service_account,
                    "threads": dbt_core_resource.threads,
                }
            },
        }


class SnowflakeDetails(DBDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.SNOWFLAKE)
    account = encrypt(models.CharField(max_length=255, blank=False))
    warehouse = encrypt(models.CharField(max_length=255, blank=False))
    database = encrypt(models.CharField(max_length=255, blank=False))
    schema = encrypt(models.CharField(max_length=255, blank=False))
    username = encrypt(models.CharField(max_length=255, blank=False))
    password = encrypt(models.CharField(max_length=255, blank=False))
    role = models.CharField(max_length=255, blank=False)


class DuckDBDetails(DBDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.DUCKDB)
    # NOTE: only works for duckdb files in the docker container for now, not S3
    path = encrypt(models.TextField(blank=False))

    @property
    def venv_path(self):
        return ".duckdbvenv"

    @property
    def datahub_extras(self):
        return ["sqlalchemy", "dbt"]

    @property
    def datahub_db_nickname(self):
        return "duckdb"

    def get_connector(self):
        return DatabaseFileConnector(path=self.path)

    def get_datahub_config(self, db_path) -> dict[str, Any]:
        return {
            "source": {
                "type": "sqlalchemy",
                "config": {
                    "connect_uri": f"datahub:///{self.path}",
                    "platform": "duckdb",
                },
            },
            "sink": get_sync_config(db_path),
        }

    def get_dbt_profile_contents(self, dbt_core_resource: DBTCoreDetails):
        return {
            "target": "dev",
            "outputs": {"dev": {"type": "duckdb", "path": self.path}},
        }


class DataFileDetails(ResourceDetails):
    subtype = models.CharField(max_length=255, default=ResourceSubtype.FILE)
    path = models.TextField(blank=False)


class WorkflowRun(models.Model):
    id = models.UUIDField(primary_key=True)
    status = models.TextField(choices=WorkflowStatus.choices, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    resource = models.ForeignKey(
        "Resource", on_delete=models.CASCADE, null=True, related_name="workflow_runs"
    )
