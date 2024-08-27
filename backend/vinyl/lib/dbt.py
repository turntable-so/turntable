## NOTE: can't name this file `dbt.py` or weird import errors will ensue.
import os
import re
import subprocess
import sys
import traceback
from dataclasses import make_dataclass
from io import StringIO
from typing import Any

import yaml
from dbt_extractor import ExtractionError, py_extract_from_source

from vinyl.lib.dbt_methods import (
    MAX_DIALECT_VERSION,
    DBTArgs,
    DBTDialect,
    DBTError,
    DBTVersion,
)
from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.utils.files import adjust_path, cd, file_exists_in_directory, load_orjson
from vinyl.lib.utils.graph import DAG


class DBTProject(object):
    compiled_sql_path: str
    manifest_path: str
    catalog_path: str
    run_results_path: str
    target_path: str
    manifest: dict[str, Any]
    model_graph: DAG
    catalog: dict[str, Any]
    profile_name: str
    dbt_profiles_dir: str
    dbt_project_yml: dict[str, Any]
    dbt1_5: bool
    max_threads: int = 4
    version: DBTVersion
    version_list: list[int]
    multitenant: bool

    def __init__(
        self,
        dbt_project_dir: str,
        dialect: DBTDialect,
        version: DBTVersion,
        dbt_profiles_dir: str | None = None,
        target_path: str | None = None,
        manifest_req: bool = False,
        catalog_req: bool = False,
        compile_exclusions: list[str] | None = None,
        env_vars: dict[str, str] = {},
    ):
        self.dbt_project_dir = adjust_path(dbt_project_dir)
        self.dialect = dialect
        self.version = version
        self.compile_exclusions = compile_exclusions
        self.env_vars = env_vars

        # set version bool
        self.version_list = [int(v[0]) for v in self.version.split(".")]
        if tuple(self.version_list) >= (1, 5):
            self.dbt1_5 = True
        else:
            self.dbt1_5 = False

        # get target paths
        if target_path:
            self.target_path = adjust_path(target_path)
            os.environ["DBT_TARGET_PATH"] = self.target_path
        else:
            self.get_project_yml_files()
        self.generate_target_paths()

        # determine tenancy
        if os.getenv("MULTITENANT") == "true":
            self.multitenant = True
        else:
            self.multitenant = False
            # self.install_dbt_if_necessary()

        # get profiles-dir
        self.dbt_profiles_dir = (
            self.get_profiles_dir() if not dbt_profiles_dir else dbt_profiles_dir
        )

        if self.needs_dbt_deps():
            self.run_dbt_command(["deps"])

        # get artifacts if required
        if manifest_req:
            self.mount_manifest()

        if catalog_req:
            self.mount_catalog()

        # validate paths
        if not os.path.exists(self.dbt_project_dir):
            raise Exception(f"Project path do not exist: {self.dbt_project_dir}")

    def install_dbt_if_necessary(self):
        dbt_package = f"dbt-{self.dialect.value.lower()}"
        install_package = f"{dbt_package}~={self.version}.0"
        res = subprocess.run(
            ["uv", "pip", "show", dbt_package, "--python", sys.executable],
            capture_output=True,
        )
        if res.returncode != 0:
            subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    install_package,
                    "--python",
                    sys.executable,
                ],
                check=True,
            )
            return

        major_version_in_stdout = (
            res.stdout.decode().split("\n")[1].split(":")[1].strip().rsplit(".", 1)[0]
        )
        if major_version_in_stdout != self.version:
            subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    install_package,
                    "--python",
                    sys.executable,
                ],
                check=True,
            )

    def generate_target_paths(self):
        if self.target_path:
            self.manifest_path = os.path.join(self.target_path, "manifest.json")
            self.catalog_path = os.path.join(self.target_path, "catalog.json")
            self.run_results_path = os.path.join(self.target_path, "run_results.json")
            self.compiled_sql_path = os.path.join(self.target_path, "compiled")
        else:
            raise Exception("Target path not found")

    def needs_dbt_deps(self):
        packages_yml_path = os.path.join(self.dbt_project_dir, "packages.yml")
        dbt_packages_path = os.path.join(self.dbt_project_dir, "dbt_packages")
        if not os.path.exists(packages_yml_path):
            return False
        if os.path.exists(dbt_packages_path) and os.listdir(dbt_packages_path):
            return False
        return True

    def mount_manifest(self, read=True, force_read=False, force_run=False):
        if hasattr(self, "manifest") and not force_run and not force_read:
            return "", "", True
        elif force_run or not os.path.exists(self.manifest_path):
            return self.dbt_parse()

        if read:
            self.manifest = load_orjson(self.manifest_path)
        elif (force_read or force_run) and hasattr(self, "manifest"):
            # make sure you don't accidentally read an outdated manifest in the future
            del self.manifest

    def build_model_graph(self, include_sources: bool = False, rebuild=False) -> DAG:
        if hasattr(self, "model_graph") and not rebuild:
            return self.model_graph
        # build networkx graph
        dag = DAG()
        for parent, children in self.manifest["child_map"].items():
            for child in children:
                dag.add_edge(parent, child)

        # build table_level dag without metric nodes
        nodes_to_remove = [
            k
            for k in dag.node_dict
            if k.startswith("metric.")
            or k.startswith("test.")
            or (
                not include_sources
                and (k.startswith("source.") or k.startswith("seed."))
            )  # only include sources and seeds in nodes to remove if include_sources is True
        ]
        dag.remove_nodes_and_reconnect(nodes_to_remove)

        self.model_graph = dag
        return dag

    def get_ancestors_and_descendants(
        self,
        node_ids: list[str],
        predecessor_depth: int | None,
        successor_depth: int | None,
    ) -> list[str]:
        self.build_model_graph(include_sources=False)
        return self.model_graph.get_ancestors_and_descendants(
            node_ids, predecessor_depth, successor_depth
        )

    def mount_catalog(self, read=True, force_run=False, force_read=False):
        if hasattr(self, "catalog") and not force_run and not force_read:
            return "", "", True
        elif force_run or not os.path.exists(self.catalog_path):
            self.dbt_docs_generate()

        if read:
            self.catalog = load_orjson(self.catalog_path)
        elif (force_read or force_run) and hasattr(self, "catalog"):
            # make sure you don't accidentally read an outdated artifact in the future
            del self.catalog

    def get_project_yml_files(self):
        with open(os.path.join(self.dbt_project_dir, "dbt_project.yml"), "r") as f:
            self.dbt_project_yml = yaml.load(f, yaml.CLoader)

        # get target path
        if hasattr(self, "target_path"):
            return
        elif "DBT_TARGET_PATH" in os.environ:
            self.target_path = os.path.join(
                self.dbt_project_dir, os.environ["DBT_TARGET_PATH"]
            )
        elif "target-path" in self.dbt_project_yml and tuple(self.version_list[:2]) <= (
            1,
            6,
        ):  # target-path deprecated in 1.7
            self.target_path = os.path.join(
                self.dbt_project_dir, self.dbt_project_yml["target-path"]
            )
        else:
            self.target_path = os.path.join(self.dbt_project_dir, "target")

    def dbt_runner(self, command: list[str]) -> tuple[str, str, bool]:
        try:
            from dbt.cli.main import dbtRunner, dbtRunnerResult
        except ImportError:
            raise Exception("dbt 1.5+ runner not installed")

        runner = dbtRunner()
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()

        # Save original streams
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr

        # Redirect streams to buffers
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer

        # Cache env variables
        current_dbt_profiles_dir = os.environ.get("DBT_PROFILES_DIR")
        os.environ["DBT_PROFILES_DIR"] = self.dbt_profiles_dir
        current_dbt_project_dir = os.environ.get("DBT_PROJECT_DIR")
        os.environ["DBT_PROJECT_DIR"] = self.dbt_project_dir

        # Invoke dbt
        result: dbtRunnerResult = runner.invoke(
            command, send_anonymous_usage_stats=False
        )

        # Restore env variables
        del os.environ["DBT_PROFILES_DIR"]
        if current_dbt_profiles_dir:
            os.environ["DBT_PROFILES_DIR"] = current_dbt_profiles_dir
        del os.environ["DBT_PROJECT_DIR"]
        if current_dbt_project_dir:
            os.environ["DBT_PROJECT_DIR"] = current_dbt_project_dir

        captured_stdout = stdout_buffer.getvalue()
        captured_stderr = stderr_buffer.getvalue()

        # Restore original streams
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

        # Return captured output along with function's result
        return captured_stdout, captured_stderr, result.success

    def dbt_cli(self, command: list[str]) -> tuple[str, str, bool]:
        env = {
            **os.environ.copy(),
            **{"DBT_PROFILES_DIR": self.dbt_profiles_dir},
            **{"DBT_TARGET_PATH": self.target_path},
            **self.env_vars,
        }
        if self.dbt1_5:
            env["DBT_PROJECT_DIR"] = self.dbt_project_dir

        result = subprocess.run(
            [
                "dbtenv",
                "--profiles-dir",
                self.dbt_profiles_dir,
                "execute",
                "--dbt",
                f"dbt-{self.dialect.value}=={MAX_DIALECT_VERSION[self.dialect.value][self.version]}",
                "--",
                *command,
            ],
            capture_output=True,
            env=env,
            text=True,
            cwd=self.dbt_project_dir if not self.dbt1_5 else None,
        )
        success = not DBTError.has_dbt_error(
            result.stdout
        ) and not DBTError.has_dbt_error(result.stderr)

        return result.stdout, result.stderr, success

    def run_dbt_command(
        self,
        command: list[str],
        cli_args: list[str] | None = None,
        write_json: bool = False,
        dbt_cache: bool = False,
        force_terminal: bool = True,  # for our purposes, terminal execution is preferred due to version isolation
    ) -> tuple[str, str, bool]:
        if cli_args is None:
            cli_args = []

        full_command = []
        if not write_json:
            full_command.append("--no-write-json")

        full_command.append("--no-use-colors")

        if not self.dbt1_5:
            full_command.append("--no-anonymous-usage-stats")

        if dbt_cache:
            pass
        elif self.dbt1_5:
            full_command.append("--no-populate-cache")
        else:
            full_command.append("--cache-selected-only")

        full_command += command + cli_args

        if (
            self.dbt1_5
            and not force_terminal
            and not os.getenv("MULTITENANT") == "true"
        ):
            stdout, stderr, success = self.dbt_runner(full_command)
        else:
            stdout, stderr, success = self.dbt_cli(full_command)

        print(stdout, stderr, success)

        if len(stderr) > 0 and not stderr.startswith("dbtenv info:"):
            success = False
        return stdout, stderr, success

    def dbt_parse(self) -> tuple[str, str, bool]:
        if self.dbt1_5:
            return self.run_dbt_command(["parse"], write_json=True)
        return self.run_dbt_command(["parse", "--write-manifest"], write_json=True)

    def dbt_compile(
        self,
        node_ids: list[str] | None = None,
        write_json: bool = True,
        dbt_cache: bool = False,
        predecessor_depth: int | None = 0,
        successor_depth: int | None = 0,
        update_manifest=False,
        models_only: bool = False,
    ) -> tuple[str, str, bool]:
        if not node_ids:
            command = ["compile", "-f"]
            node_ids = []
        else:
            command = ["compile", "-f", "-s"]
            full_node_list = self.get_ancestors_and_descendants(
                node_ids, predecessor_depth, successor_depth
            )
            command += [v.split(".")[-1] for v in full_node_list]

        if models_only:
            command.append("--exclude")
            command.append("test_type:singular")
            command.append("test_type:generic")

        # don't exclude node if explicitly provided
        adj_exclusions = (
            list(
                set(self.compile_exclusions)
                - set([id.split(".")[-1] for id in node_ids])
            )
            if self.compile_exclusions
            else []
        )
        if adj_exclusions:
            if "--exclude" not in command:
                command.append("--exclude")
            command.extend(self.compile_exclusions)

        stdout, stderr, success = self.run_dbt_command(
            command, write_json=write_json, dbt_cache=dbt_cache
        )
        if update_manifest:
            self.mount_manifest(force_read=True)
        return stdout, stderr, success

    def dbt_docs_generate(self, compile=False) -> tuple[str, str, bool]:
        if compile:
            stdout, stderr, success = self.run_dbt_command(
                ["docs", "generate"], write_json=True, dbt_cache=True
            )
            return stdout, stderr, success

        stdout, stderr, success = self.run_dbt_command(
            ["docs", "generate", "--no-compile"], write_json=True, dbt_cache=True
        )
        return stdout, stderr, success

    def get_compiled_sql(
        self,
        node_id: str,
        force_read: bool = False,
        errors: list[VinylError] = [],
        compile_if_not_found: bool = True,
    ) -> tuple[str | None, list[VinylError]]:
        self.mount_manifest(force_read=force_read)
        if node_id in self.manifest["nodes"]:
            node = self.manifest["nodes"][node_id]
        elif (
            node_id in self.manifest["disabled"]
            and len(self.manifest["disabled"][node_id]) > 0
        ):
            node = self.manifest["disabled"][node_id][0]

        else:
            node = None

        if node is None:
            errors.extend(
                [
                    VinylError(
                        node_id=node_id,
                        type=VinylErrorType.FILE_NOT_FOUND,
                        msg=f"Node not found: {node_id.split('.')[-1]}",
                        traceback=None,
                        dialect=self.dialect,
                    )
                ]
            )
            return None, errors

        compiled_sql_abs_location = os.path.join(
            self.compiled_sql_path,
            node_id.split(".")[1],
            node["original_file_path"],
        )

        try:
            if not os.path.exists(compiled_sql_abs_location) and compile_if_not_found:
                stdout, stderr, success = self.dbt_compile(
                    [node_id], write_json=True, dbt_cache=False, update_manifest=False
                )
            with open(compiled_sql_abs_location, "r") as f:
                out = f.read()
            return out, errors

        except FileNotFoundError:
            msg = f"Compiled SQL not found for {node_id.split('.')[-1]}"
            if locals().get("stdout", None):
                msg += f". DBT output: {stdout}"
            errors.extend(
                [
                    VinylError(
                        node_id=node_id,
                        type=VinylErrorType.FILE_NOT_FOUND,
                        msg=msg,
                        traceback=traceback.format_exc(),
                        dialect=self.dialect,
                    )
                ]
            )
            return None, errors

    def get_profiles_dir(self):
        if "DBT_PROFILES_DIR" in os.environ:
            return os.environ["DBT_PROFILES_DIR"]

        in_directory_path = os.path.join(self.dbt_project_dir, "profiles.yml")
        if os.path.exists(in_directory_path):
            return os.path.dirname(in_directory_path)

        in_home_path = os.path.join(os.path.expanduser("~"), ".dbt", "profiles.yml")
        if os.path.exists(in_home_path):
            return os.path.dirname(in_home_path)

        raise Exception("Could not find profiles.yml file")

    def get_profile_credentials(self, via_dbt=True):
        dbt_profiles_dir = self.get_profiles_dir()
        profile_name = self.dbt_project_yml["profile"]
        with cd(self.dbt_project_dir):
            if via_dbt:
                # import relevant dbt modules
                from dbt.config import RuntimeConfig
                from dbt.flags import set_from_args

                # generate bq connection object
                _args = DBTArgs(
                    dbt_profiles_dir, self.dbt_project_dir, None, None, {}, None
                )
                set_from_args(_args.to_namespace(), _args)
                dbt_project, dbt_profile = RuntimeConfig.collect_parts(_args)
                _profile = dbt_profile
                _config = RuntimeConfig.from_parts(dbt_project, dbt_profile, _args)
                credentials = _config.credentials
            else:
                with open(f"{dbt_profiles_dir}/profiles.yml", "r") as f:
                    contents = yaml.load(f, yaml.CLoader)
                target_name = contents[profile_name]["target"]
                target = contents[profile_name]["outputs"][target_name]
                dataclsname = self.dialect.get_dbt_credentials_dataclass_name()
                fields = [
                    ("method", str | None),
                    ("database", str | None),
                    ("schema", str | None),
                    ("username", str | None),
                    ("password", str | None),
                    ("host", str | None),
                    ("port", int | None),
                    ("keyfile", str | None),
                    ("keyfile_json", str | None),
                    ("path", str | None),
                ]
                datacls = make_dataclass(dataclsname, fields)
                credentials = datacls(
                    method=target.get("method", None),
                    database=target.get("database", None),
                    schema=target.get(
                        "schema", target.get("dataset", None)
                    ),  # bigquery allows for dataset
                    username=target.get("user", None),
                    password=target.get("password", None),
                    host=target.get("host", None),
                    port=target.get("port", None),
                    keyfile=target.get("keyfile", None),
                    keyfile_json=target.get("keyfile_json", None),
                    path=target.get("path", None),
                )
        return credentials

    def get_relation_name(
        self,
        node_name: str,
    ) -> str | None:
        node_header = node_name.split(".")[0]
        if node_header == "source":
            manifest_key = "sources"
        elif (
            node_header == "model" or node_header == "snapshot" or node_header == "seed"
        ):
            manifest_key = "nodes"
        elif node_header in ["metric", "test"]:
            # these nodes aren't materialized
            return None
        else:
            raise Exception(f"Node type not recognized: {node_header}")
        node = self.manifest[manifest_key][node_name]
        if node.get("relation_name", None) is not None:
            relation_name = node["relation_name"]
        else:
            if (
                node.get("database", None) is not None
                and node.get("schema", None) is not None
                and node.get("name", None) is not None
            ):
                if node.get("alias", None) is not None:
                    tbl_name = node["alias"]
                else:
                    tbl_name = node["name"]
                if self.dialect in ["bigquery", "databricks"]:
                    relation_name = (
                        f"`{node['database']}`.`{node['schema']}`.`{tbl_name}`"
                    )
                else:
                    relation_name = f"{node['database']}.{node['schema']}.{tbl_name}"
            else:
                return None
        return relation_name


def install_dbt_version(
    dialect: DBTDialect,
    major_version: DBTVersion,
):
    need_to_install = False
    try:
        from dbt import version

        version_diff = (
            version.__version__.split(".")[:2] != major_version.value.split(".")[:2]
        )
        if version_diff:
            need_to_install = True

    except ImportError:
        need_to_install = True

    if need_to_install:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"dbt-{dialect.value}~={major_version.value}.0",
            ],
            capture_output=True,
            text=True,
        )
    if not need_to_install or result.returncode == 0:
        return True
    return False


def run_adjusted_replace(base_pattern_list, replacement, contents):
    pattern = r"\s*".join(base_pattern_list)
    adjusted_pattern = pattern
    return re.sub(adjusted_pattern, replacement, contents)


def replace_sources_and_refs(project: DBTProject, contents):
    try:
        project.mount_manifest()
        project.get_project_yml_files()

        extracted = py_extract_from_source(contents)
        new_contents = contents
        manifest_info = project.manifest
        nodes = manifest_info["nodes"]
        sources = manifest_info["sources"]
        proj_name = project.dbt_project_yml["name"]
        macro_dir = os.path.join(project.dbt_project_dir, "macros")
        # check if user has custom ref macro
        if not file_exists_in_directory("ref.sql", macro_dir):
            for ref in extracted["refs"]:
                model_name = ref["name"]
                package_name = ref.get("package", proj_name)
                base_pattern_list = [
                    r"{{",
                    r"ref",
                    r"\(",
                    r"[\"']",
                    re.escape(model_name),
                    r"[\"']",
                    r"\)",
                    r"}}",
                ]
                node_id = f"model.{package_name}.{model_name}"
                if node_id in nodes:
                    replacement = project.get_relation_name(node_id)
                    new_contents = run_adjusted_replace(
                        base_pattern_list, replacement, new_contents
                    )

        # check if user has custom source macro
        if not file_exists_in_directory("source.sql", macro_dir):
            for source in extracted["sources"]:
                base_pattern_list = [
                    r"{{",
                    r"source",
                    r"\(",
                    r"[\"']",
                    re.escape(source[0]),
                    r"[\"']",
                    r",",
                    r"[\"']",
                    re.escape(source[1]),
                    r"[\"']",
                    r"\)",
                    r"}}",
                ]
                source_id = f"source.{proj_name}.{source[0]}.{source[1]}"
                if source_id in sources:
                    replacement = project.get_relation_name(source_id)
                    new_contents = run_adjusted_replace(
                        base_pattern_list, replacement, new_contents
                    )
        return new_contents

    except ExtractionError:
        return contents


def replace_configs_and_this(
    project: DBTProject, contents, model_node_string: str | None = None
):
    try:
        project.mount_manifest()
        project.get_project_yml_files()

        new_contents = contents
        pattern = r"{{\s*config\s*\([\s\S]*?\)\s*}}"
        new_contents = re.sub(
            pattern, lambda x: "", new_contents, flags=re.MULTILINE | re.DOTALL
        )
        if model_node_string is not None:
            base_pattern_list = [
                r"{{",
                r"this",
                r"}}",
            ]
            replacement = project.get_relation_name(model_node_string)
            new_contents = run_adjusted_replace(
                base_pattern_list, replacement, new_contents
            )
        return new_contents

    except ExtractionError:
        return contents


def fast_compile(project: DBTProject, dbt_sql: str):
    contents = replace_sources_and_refs(project, dbt_sql)
    contents = replace_configs_and_this(project, contents)
    return contents
