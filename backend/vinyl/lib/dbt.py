## NOTE: can't name this file `dbt.py` or weird import errors will ensue.
import os
import re
import select
import subprocess
import sys
import tempfile
import traceback
from dataclasses import make_dataclass
from io import StringIO
from typing import Any, Callable, Generator

import orjson
import yaml
from dbt_extractor import ExtractionError, py_extract_from_source

from vinyl.lib.dbt_methods import (
    DBTArgs,
    DBTDialect,
    DBTError,
    DBTVersion,
)
from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.utils.env import set_env
from vinyl.lib.utils.files import adjust_path, cd, file_exists_in_directory, load_orjson
from vinyl.lib.utils.graph import DAG
from vinyl.lib.utils.patch import patch_json_with_orjson, patch_yaml_with_libyaml
from vinyl.lib.utils.query_limit_helper import query_limit_helper

STREAM_SUCCESS_STRING = "PROCESS_STREAM_SUCCESS"
STREAM_ERROR_STRING = "PROCESS_STREAM_ERROR"


def run_adjusted_replace(base_pattern_list, replacement, contents):
    pattern = r"\s*".join(base_pattern_list)
    adjusted_pattern = pattern
    return re.sub(adjusted_pattern, replacement, contents)


class DBTProject(object):
    compiled_sql_path: str
    manifest_path: str
    catalog_path: str
    run_results_path: str
    target_path: str
    manifest: dict[str, Any]
    model_graph: DAG
    macro_graph: DAG
    catalog: dict[str, Any]
    profile_name: str
    dbt_profiles_dir: str
    dbt_project_yml: dict[str, Any]
    dbt1_5: bool
    max_threads: int = 4
    version: DBTVersion
    version_list: list[int]
    deferral_target_path: str | None

    supported_api_versions = [DBTVersion.V1_8]
    supported_api_dialects = [
        DBTDialect.BIGQUERY,
        DBTDialect.SNOWFLAKE,
        DBTDialect.POSTGRES,
        DBTDialect.REDSHIFT,
        DBTDialect.DUCKDB,
    ]  # databricks not currently supported due to package conflicts

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
        deferral_target_path: str | None = None,
    ):
        self.dbt_project_dir = adjust_path(dbt_project_dir)
        self.dialect = dialect
        self.version = version
        self.compile_exclusions = compile_exclusions
        self.env_vars = env_vars
        self.deferral_target_path = deferral_target_path

        # set version bool
        self.version_list = [int(v[0]) for v in self.version.split(".")]
        if tuple(self.version_list) >= (1, 5):
            self.dbt1_5 = True
        else:
            self.dbt1_5 = False

        # get target paths
        if target_path:
            self.target_path = adjust_path(target_path)
        else:
            self.get_project_yml_files()
        self.generate_target_paths()

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
            [
                sys.executable,
                "-m",
                "uv",
                "pip",
                "show",
                dbt_package,
            ],
            capture_output=True,
        )
        major_version_in_stdout = (
            (res.stdout.decode().split("\n")[1].split(":")[1].strip().rsplit(".", 1)[0])
            if res.stdout
            else None
        )
        if res.returncode != 0 or major_version_in_stdout != self.version:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    install_package,
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

    def mount_manifest(
        self, read=True, force_read=False, force_run=False, defer: bool = False
    ):
        if hasattr(self, "manifest") and not force_run and not force_read:
            return self.manifest
        elif force_run or not os.path.exists(self.manifest_path):
            stdout, stderr, success = self.dbt_parse(defer=defer)
            if not success:
                raise Exception(
                    f"Failed to parse manifest. Stdout: {stdout}, Stderr: {stderr}"
                )

        if read:
            self.manifest = load_orjson(self.manifest_path)

        elif (force_read or force_run) and hasattr(self, "manifest"):
            # make sure you don't accidentally read an outdated manifest in the future
            del self.manifest

        return self.manifest

    def build_macro_graph(self, rebuild=False) -> DAG:
        self.mount_manifest()
        self.macro_graph = DAG()
        for k, v in self.manifest["macros"].items():
            self.macro_graph.add_node(k)
            for dep in v["depends_on"]["macros"]:
                self.macro_graph.add_edge(dep, k)
        return self.macro_graph

    def build_model_graph(self, include_sources: bool = False, rebuild=False) -> DAG:
        self.mount_manifest()
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
            or k.startswith("semantic_model.")
            or k.startswith("saved_query.")
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
        self.mount_manifest()
        self.build_model_graph(include_sources=False)
        return self.model_graph.get_ancestors_and_descendants(
            node_ids, predecessor_depth, successor_depth
        )

    def mount_catalog(
        self,
        read=True,
        force_run=False,
        force_read=False,
        defer: bool = False,
        partial: bool = False,
        partial_nodes: list[str] | None = None,
    ):
        if hasattr(self, "catalog") and not force_run and not force_read:
            return self.catalog
        elif force_run or not os.path.exists(self.catalog_path):
            _, _, success = self.dbt_docs_generate(
                defer=defer, partial=partial, partial_nodes=partial_nodes
            )
            if not success:
                raise Exception("Failed to generate catalog")
        if read:
            if defer:
                self.catalog = load_orjson(
                    os.path.join(self.deferral_target_path, "catalog.json")
                )
                new_catalog = load_orjson(self.catalog_path)
                for key in ["nodes", "sources", "errors"]:
                    new_val = new_catalog.get(key)
                    if self.catalog.get(key) is None:
                        self.catalog[key] = new_val
                    else:
                        self.catalog[key].update(new_val)
            else:
                self.catalog = load_orjson(self.catalog_path)
        elif (force_read or force_run) and hasattr(self, "catalog"):
            # make sure you don't accidentally read an outdated artifact in the future
            del self.catalog

        return self.catalog

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

    @property
    def can_use_dbt_api(self) -> bool:
        adjusted_supported_api_versions = self.supported_api_versions + [
            v.value for v in self.supported_api_versions
        ]
        adjusted_supported_api_dialects = self.supported_api_dialects + [
            v.value for v in self.supported_api_dialects
        ]
        return (
            self.version in adjusted_supported_api_versions
            and self.dialect in adjusted_supported_api_dialects
        )

    @patch_json_with_orjson
    @patch_yaml_with_libyaml
    def dbt_runner(self, command: list[str]) -> tuple[str, str, bool]:
        env, cwd = self._dbt_cli_env(full_os_env=False)

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
        orig_cwd = os.getcwd()

        # Redirect streams to buffers
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        try:
            with set_env(**env):
                # Invoke dbt
                result: dbtRunnerResult = runner.invoke(
                    command, send_anonymous_usage_stats=False
                )
                captured_stdout = stdout_buffer.getvalue()
                captured_stderr = stderr_buffer.getvalue()

                # Return captured output along with function's result
                return captured_stdout, captured_stderr, result.success

        finally:
            # Restore original streams
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

            ## DBT changes directory sometimes, so we need to restore the original directory
            ## DBT has an internal bug where cwd is still set to a directory after its function call. We use temp directories, so this can cause an error if the temp directory no longer exists.
            try:
                current_dir = os.getcwd()
            except OSError:
                current_dir = None

            ## restore original directory if everything fails.
            if not current_dir or current_dir != orig_cwd:
                os.chdir(orig_cwd)

    def _dbt_cli_env(self, full_os_env: bool = True):
        env = self.env_vars.copy()
        if self.dbt_profiles_dir:
            env["DBT_PROFILES_DIR"] = self.dbt_profiles_dir
        if self.target_path:
            env["DBT_TARGET_PATH"] = self.target_path
        if self.version:
            env["DBT_VERSION"] = self.version
        if full_os_env:
            env = {**os.environ, **env}
        if self.dbt1_5:
            env["DBT_PROJECT_DIR"] = self.dbt_project_dir
            cwd = None
        else:
            cwd = self.dbt_project_dir
        return env, cwd

    def dbt_cli(self, command: list[str]) -> tuple[str, str, bool]:
        env, cwd = self._dbt_cli_env()
        out = subprocess.run(
            ["dbtx", *command], env=env, cwd=cwd, text=True, capture_output=True
        )
        success = self.check_command_success(out.stdout, out.stderr)

        return out.stdout, out.stderr, success

    def dbt_cli_stream(
        self, command: list[str], should_terminate: Callable[[], bool] = None
    ) -> Generator[str, None, tuple[str, str, bool]]:
        env, cwd = self._dbt_cli_env()

        stdouts = []
        stderrs = []
        process = subprocess.Popen(
            ["dbtx", *command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            cwd=cwd,
        )

        while process.poll() is None:
            if should_terminate is not None and should_terminate():
                process.terminate()
                return
            ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
            for stream in ready:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        stdouts.append(line)
                    else:
                        stderrs.append(line)
                    yield line

        # Read any remaining output after termination
        if process.stdout:
            for line in process.stdout:
                stdouts.append(line)
                yield line
        if process.stderr:
            for line in process.stderr:
                stderrs.append(line)
                yield line

        stdout = "".join(stdouts)
        stderr = "".join(stderrs)

        success = self.check_command_success(stdout, stderr)
        success_str = STREAM_SUCCESS_STRING if success else STREAM_ERROR_STRING
        yield success_str

    @classmethod
    def check_command_success(cls, stdout: str, stderr: str) -> bool:
        success = not DBTError.has_dbt_error(stdout) and not DBTError.has_dbt_error(
            stderr
        )
        if len(stderr) > 0:
            installation_pattern = r"^Installed \d+ packages? in \d+(?:\.\d+)?\s*\w+$"
            if not re.match(installation_pattern, stderr.strip()):
                success = False
        return success

    def get_dbt_command(
        self,
        command: list[str],
        cli_args: list[str] | None = None,
        write_json: bool = False,
        dbt_cache: bool = False,
        defer: bool = False,
        defer_selection: bool = True,
        use_colors: bool = False,
    ) -> tuple[str, str, bool]:
        if cli_args is None:
            cli_args = []

        full_command = []
        if not write_json:
            full_command.append("--no-write-json")

        if not use_colors:
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

        if defer and full_command[0] in [
            "parse",
            "compile",
            "docs",
            "run",
            "test",
            "build",
        ]:
            if self.deferral_target_path is None:
                raise Exception("Deferral target path not set")
            if defer_selection and full_command[0] != "parse":
                full_command.extend(["-s", "state:modified+"])
            full_command.extend(
                [
                    "--defer",
                    "--state",
                    self.deferral_target_path,
                ]
            )

        return full_command

    def run_dbt_command(
        self,
        command: list[str],
        cli_args: list[str] | None = None,
        write_json: bool = False,
        dbt_cache: bool = False,
        force_terminal: bool = True,
        defer: bool = False,
        defer_selection: bool = True,
    ) -> tuple[str, str, bool]:
        full_command = self.get_dbt_command(
            command,
            cli_args,
            write_json,
            dbt_cache,
            defer,
            defer_selection,
        )
        if self.can_use_dbt_api and not force_terminal:
            return self.dbt_runner(full_command)

        else:
            return self.dbt_cli(full_command)

    def stream_dbt_command(
        self,
        command: list[str],
        should_terminate: Callable[[], bool] = None,
        cli_args: list[str] | None = None,
        write_json: bool = False,
        dbt_cache: bool = False,
        force_terminal: bool = True,
        defer: bool = False,
        defer_selection: bool = True,
    ) -> Generator[str, None, tuple[str, str, bool]]:
        full_command = self.get_dbt_command(
            command=command,
            cli_args=cli_args,
            write_json=write_json,
            dbt_cache=dbt_cache,
            defer=defer,
            defer_selection=defer_selection,
            use_colors=True,
        )
        if self.can_use_dbt_api and not force_terminal:
            # self.install_dbt_if_necessary()
            # TODO: make streaming work for python api
            yield from self.dbt_cli_stream(
                full_command, should_terminate=should_terminate
            )
        else:
            yield from self.dbt_cli_stream(
                full_command, should_terminate=should_terminate
            )

    def dbt_parse(self, defer: bool = False) -> tuple[str, str, bool]:
        if self.dbt1_5:
            return self.run_dbt_command(["parse"], write_json=True, defer=defer)
        return self.run_dbt_command(
            ["parse", "--write-manifest"], write_json=True, defer=defer
        )

    def dbt_compile(
        self,
        node_ids: list[str] | None = None,
        write_json: bool = True,
        dbt_cache: bool = False,
        predecessor_depth: int | None = 0,
        successor_depth: int | None = 0,
        update_manifest=False,
        models_only: bool = False,
        defer: bool = False,
        defer_selection: bool = True,
        exclude_introspective: bool = False,
        fast_compile: bool = False,
    ) -> tuple[str, str, bool]:
        if not node_ids:
            command = ["compile", "-f"]
            node_ids = []
        else:
            command = ["compile", "-f", "-s"]
            full_node_list = self.get_ancestors_and_descendants(
                node_ids, predecessor_depth, successor_depth
            )
            adj_full_node_list = []
            if fast_compile:
                for node_id in full_node_list:
                    sql = self.fast_compile_node(node_id)
                    if sql is None:
                        adj_full_node_list.append(node_id)
            else:
                adj_full_node_list = full_node_list

            if len(adj_full_node_list) == 0:
                return "", "", True

            command += [v.split(".")[-1] for v in adj_full_node_list]

        # determine exclusions
        if models_only:
            command.append("--exclude")
            command.append("test_type:singular")
            command.append("test_type:generic")

        adj_exclusions = (
            set(self.compile_exclusions) if self.compile_exclusions else set()
        )
        if exclude_introspective:
            adj_exclusions |= set(self.get_introspective_models())

        if adj_exclusions:
            ## don't exclude node if explicitly provided
            adj_exclusions -= set([id_.split(".")[-1] for id_ in node_ids])
        if adj_exclusions:
            if "--exclude" not in command:
                command.append("--exclude")
            command.extend(adj_exclusions)

        stdout, stderr, success = self.run_dbt_command(
            command,
            write_json=write_json,
            dbt_cache=dbt_cache,
            defer=defer,
            defer_selection=defer_selection,
        )
        if update_manifest:
            self.mount_manifest(force_read=True, defer=defer)
        return stdout, stderr, success

    def dbt_docs_generate(
        self,
        compile=False,
        defer: bool = False,
        partial: bool = False,
        partial_nodes: list[str] | None = None,
    ) -> tuple[str, str, bool]:
        command = ["docs", "generate"]
        if compile:
            command += ["--no-compile"]

        if (
            partial
            and tuple(self.version_list) >= (1, 7)
            and partial_nodes
            and len(partial_nodes) > 0
        ):
            command += ["-s"]
            command += partial_nodes

        return self.run_dbt_command(command, dbt_cache=True, defer=defer)

    def get_compiled_sql(
        self,
        node_id: str,
        force_read: bool = False,
        errors: list[VinylError] = [],
        compile_if_not_found: bool = True,
        defer: bool = False,
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

        if "compiled_code" in node:
            return node["compiled_code"], errors

        compiled_sql_abs_location = os.path.join(
            self.compiled_sql_path,
            node_id.split(".")[1],  # project_name
            node["original_file_path"],
        )

        if os.path.exists(compiled_sql_abs_location):
            with open(compiled_sql_abs_location, "r") as f:
                out = f.read()
            return out, errors

        elif defer:
            # should be in the same file spot in the deferred project. Otherwise, file has changed and would show up in compile above.
            deferral_compiled_sql_abs_location = os.path.join(
                self.deferral_target_path,
                "compiled",
                node_id.split(".")[1],  # project_name
                node["original_file_path"],
            )

            if os.path.exists(deferral_compiled_sql_abs_location):
                with open(deferral_compiled_sql_abs_location, "r") as f:
                    out = f.read()
                return out, errors

        elif compile_if_not_found:
            stdout, stderr, success = self.dbt_compile(
                [node_id],
                write_json=True,
                dbt_cache=False,
                update_manifest=False,
                defer=defer,
            )
            if os.path.exists(compiled_sql_abs_location):
                with open(compiled_sql_abs_location, "r") as f:
                    out = f.read()
                return out, errors

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

    def preview(
        self,
        dbt_sql: str,
        limit: int | None = None,
        defer: bool = False,
        data: bool = True,
    ):
        if not self.dbt1_5:
            raise ValueError("Must use dbt 1.5+ to use show")
        if limit and not data:
            dbt_sql = query_limit_helper(dbt_sql, limit)
        command = [
            "show" if data else "compile",
            "--inline",
            dbt_sql,
            "--output",
            "json",
            "--log-level",
            "warn",
            "--log-level-file",
            "info",
            "--log-format-file",
            "json",
        ]
        if limit and data:
            command.extend(["--limit", str(limit)])
        with tempfile.TemporaryDirectory() as temp_dir:
            command.extend(["--log-path", temp_dir])
            stdout, stderr, success = self.run_dbt_command(
                command,
                write_json=False,
                dbt_cache=False,
                defer=defer,
                defer_selection=False,
            )
            if not success:
                raise Exception(
                    f"DBT show command failed.\nStderr: {stderr}\nStdout: {stdout}"
                )
            log_file = os.path.join(temp_dir, "dbt.log")
            with open(log_file, "r") as f:
                last_line = f.readlines()[-1]
                contents = orjson.loads(last_line)
            return contents["data"]["preview"] if data else contents["data"]["compiled"]

    def _replace_sources_and_refs(self, contents):
        self.mount_manifest()
        self.get_project_yml_files()
        try:
            extracted = py_extract_from_source(contents)
        except ExtractionError:
            return contents

        new_contents = contents
        manifest_info = self.manifest
        nodes = manifest_info["nodes"]
        sources = manifest_info["sources"]
        proj_name = self.dbt_project_yml["name"]
        macro_dir = os.path.join(self.dbt_project_dir, "macros")
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
                    replacement = self.get_relation_name(node_id)
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
                    replacement = self.get_relation_name(source_id)
                    new_contents = run_adjusted_replace(
                        base_pattern_list, replacement, new_contents
                    )
        return new_contents

    def _replace_configs_and_this(
        self, contents: str, model_node_string: str | None = None
    ):
        self.mount_manifest()
        self.get_project_yml_files()

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
            replacement = self.get_relation_name(model_node_string)
            new_contents = run_adjusted_replace(
                base_pattern_list, replacement, new_contents
            )
        return new_contents

    def fast_compile(self, dbt_sql: str):
        self.mount_manifest()

        # fast compile not worth it unless we have a manifest
        if not hasattr(self, "manifest") or self.manifest is None:
            return None

        if not dbt_sql:
            raise ValueError("dbt_sql is empty")
        contents = self._replace_sources_and_refs(dbt_sql)
        contents = self._replace_configs_and_this(contents)
        # if there are still jinja vars, then we failed to fast compile
        if "{{" in contents:
            return None
        return contents

    def fast_compile_node(self, node_id: str) -> str | None:
        self.mount_manifest()
        model_path = self.manifest["nodes"].get(node_id, {}).get("original_file_path")
        if not model_path:
            return None
        model_abs_path = os.path.join(self.dbt_project_dir, model_path)
        with open(model_abs_path, "r") as f:
            dbt_sql = f.read()
        sql = self.fast_compile(dbt_sql)
        if sql:
            compiled_sql_abs_path = os.path.join(
                self.compiled_sql_path,
                node_id.split(".")[1],
                model_path,
            )
            print(compiled_sql_abs_path)
            with open(compiled_sql_abs_path, "w") as f:
                f.write(sql)
            return sql
        return None

    def get_introspective_models(self):
        self.build_macro_graph()
        run_query_macros = set(self.macro_graph.get_relatives(["macro.dbt.statement"]))
        project = self.manifest["metadata"]["project_name"]
        introspective_models = []
        for node_id, node in self.manifest["nodes"].items():
            if node["resource_type"] != "model" or node["package_name"] != project:
                continue
            macros = node["depends_on"]["macros"]
            if set(macros) & run_query_macros:
                introspective_models.append(node_id.split(".")[-1])
        return introspective_models


class DBTTransition:
    before: DBTProject
    after: DBTProject
    defer: bool

    def __init__(
        self,
        before_project: DBTProject,
        after_project: DBTProject,
    ):
        self.before = before_project
        self.after = after_project
        self.after.deferral_target_path = before_project.target_path

    def docs_generate(self, compile: bool = False, defer: bool = False):
        self.before.docs_generate(compile=compile)
        self.after.docs_generate(compile=compile, defer=defer)

    def mount_manifest(
        self,
        read: bool = True,
        force_run: bool = False,
        force_read: bool = False,
        defer: bool = False,
    ):
        self.before.mount_manifest()
        self.after.mount_manifest(read=read, force_run=force_run, force_read=force_read)

    def mount_catalog(
        self,
        read: bool = False,
        force_run: bool = False,
        force_read: bool = False,
        defer: bool = False,
        partial: bool = False,
        partial_nodes: list[str] | None = None,
    ):
        self.before.mount_catalog()
        self.after.mount_catalog(
            read=read,
            force_run=force_run,
            force_read=force_read,
            defer=defer,
            partial=partial,
            partial_nodes=partial_nodes,
        )
