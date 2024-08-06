import inspect
import json
import os
from typing import Any

import ibis.expr.datatypes
import typer
from rich.console import Console
from rich.table import Table
from tqdm import tqdm
from vinyl.lib.connect import (
    DatabaseFileConnector,
    SourceInfo,
    _DatabaseConnector,
    _FileConnector,
    _TableConnector,
)
from vinyl.lib.definitions import _load_project_defs
from vinyl.lib.project import Project
from vinyl.lib.settings import _get_project_module_name, _load_project_module
from vinyl.lib.source import _get_twin_relative_path
from vinyl.lib.utils.ast import (
    _find_classes_and_attributes,
    _get_imports_from_file_regex,
)
from vinyl.lib.utils.files import _create_dirs_with_init_py, ruff_format_text
from vinyl.lib.utils.functions import _with_modified_env
from vinyl.lib.utils.obj import (
    is_valid_class_name,
    table_to_python_class,
    to_valid_class_name,
)
from vinyl.lib.utils.text import _make_python_identifier, _replace_with_dict

console = Console()


sources_cli = typer.Typer(pretty_exceptions_show_locals=False)


@sources_cli.command("list")
def list_sources(tables: bool = False):
    """Caches sources to a local directory (default: .turntable/sources)"""
    defs = _load_project_defs()
    project = Project(resources=defs.resources, models=defs.models)

    table = Table("Name", "Resource", "Location", title="Sources")
    for source in project._get_source_objects()[0]:
        if source._parent_resource is None:
            raise ValueError("Source must have a parent resource.")
        table.add_row(
            f"[bold]{source._name}[bold]",
            f"[grey70]{source._parent_resource.def_.__name__}[grey70]",
            f"[grey70]{source._location}[grey70]",
        )
    console.print(table)


def get_type_class_replace_dict():
    types = ibis.expr.datatypes
    to_replace = [k for k, v in types.__dict__.items() if inspect.isclass(v)]
    return {f"{k}(": f"t.{k}(" for k in to_replace}


def source_to_class_string(
    source: SourceInfo,
    saved_attributes: dict[str, str],
    generate_twin: bool = False,
    root_path: str | None = None,
    sample_size: int = 1000,
    twin: bool = False,
) -> str:
    if not root_path:
        module_file = _load_project_module().__file__
        if module_file is None:
            raise ValueError("Unable to find the module path for the current project")

    class_name = table_to_python_class(source._name)
    class_body = f'    _table = "{source._name}"\n'
    pr = source._parent_resource
    proj_name = _get_project_module_name()

    if pr is None:
        raise ValueError("Source must have a parent resource.")

    if isinstance(pr.connector, _TableConnector):
        if twin:
            tbl = pr.connector._get_table(source._location)
        class_body += (
            f'    _unique_name = "{proj_name}.sources.{pr.name}.{class_name}"\n'
        )

    elif isinstance(pr.connector, _DatabaseConnector):
        # source is a database
        database, schema = source._location.split(".")
        class_body += f'    _unique_name = "{proj_name}.sources.{pr.name}.{_make_python_identifier(database)}.{_make_python_identifier(schema)}.{class_name}"\n'
        class_body += f'    _schema = "{schema}"\n'
        class_body += f'    _database = "{database}"\n'

        database, schema = source._location.split(".")
        if twin:
            tbl = pr.connector._get_table(database, schema, source._name)
        class_body += (
            f'    _twin_path = "{_get_twin_relative_path(pr.name, database, schema)}"\n'
        )
        # need row count if using local files (since sampling is done live from the file)

    else:
        raise NotImplementedError(
            f"Connector type {type(pr.connector)} is not yet supported"
        )

    # need row count if using local files (since sampling is done live from the file)
    if isinstance(pr.connector, _FileConnector):
        if isinstance(pr.connector, DatabaseFileConnector):
            # in this case, location is not the real path, but the database and schema, but we can use the path from the connector
            path = os.path.relpath(pr.connector._path, root_path)
        else:
            path = os.path.relpath(source._location, root_path)
        class_body += f'    _path = "{path}"\n'
        if not pr.connector._remote and twin:
            try:
                count = tbl.count().execute()
                # in this case, we will not be caching the table, so we need the row_count
            except Exception:
                try:
                    # try to count the first column
                    first_col = tbl.columns[0]
                    count = tbl.aggregate(tbl[first_col].count()).execute().iloc[0, 0]
                except Exception:
                    # if we can't get the row count, we will just use a small default value, so we get a full sample
                    count = 0.01
            class_body += f"    _row_count = {count}\n"

    if source._schema is None:
        raise ValueError(f"Schema for {source._name} is not available")

    col_body = ""
    prev_replacements: list[str] = []
    col_replace_dict = {}
    types_replace_dict = get_type_class_replace_dict()
    for col_name, col_type in source._schema.items():
        if not is_valid_class_name(col_name):
            old_col_name = col_name
            col_name = to_valid_class_name(old_col_name, prev_replacements)
            prev_replacements.append(col_name)
            col_replace_dict[col_name] = old_col_name

        # get the string representation of the type, replacing each standard type with t.type
        col_type_str = str(col_type.__repr__())
        col_type_str = _replace_with_dict(col_type_str, types_replace_dict)
        col_type_str = _replace_with_dict(
            col_type_str,
            {"'t.Struct": "t.Struct", "t.Struct(": "t.Struct.from_tuples("},
        )  # special case for Struct, fixes bug in repr with extra quote

        base = f"    {col_name}: {col_type_str}"
        if col_name in saved_attributes:
            base += f" = {saved_attributes[col_name]}"
        col_body += f"{base}\n"

    class_body += f"    _col_replace = {json.dumps(col_replace_dict)}" + "\n\n"
    class_body += col_body

    out = f"""class {class_name}:
{class_body}
"""
    return out


def source_to_class_dict(
    source: SourceInfo,
    saved_attributes: dict[str, str],
    generate_twin: bool = False,
    root_path: str | None = None,
    sample_size: int = 1000,
    twin: bool = False,
) -> dict[str, Any]:
    if not root_path:
        module_file = _load_project_module().__file__
        if module_file is None:
            raise ValueError("Unable to find the module path for the current project")

    out: dict[str, Any] = {}
    out["config"] = {}
    out["name"] = table_to_python_class(source._name)
    out["config"]["table"] = source._name
    out["resource_name"] = source._parent_resource.name
    pr = source._parent_resource

    proj_name = _get_project_module_name()

    if pr is None:
        raise ValueError("Source must have a parent resource.")

    if isinstance(pr.connector, _TableConnector):
        if twin:
            tbl = pr.connector._get_table(source._location)
        out["unique_name"] = f"{proj_name}.sources.{pr.name}.{out['name']}"

    elif isinstance(pr.connector, _DatabaseConnector):
        # source is a database
        database, schema = source._location.split(".")
        out["unique_name"] = (
            f"{proj_name}.sources.{pr.name}.{_make_python_identifier(database)}.{_make_python_identifier(schema)}.{out['name']}"
        )
        out["read_only"] = True
        out["type"] = "source"
        out["config"]["table_schema"] = schema
        out["config"]["database"] = database

        database, schema = source._location.split(".")
        if twin:
            tbl = pr.connector._get_table(database, schema, source._name)
        out["config"]["twin_path"] = _get_twin_relative_path(pr.name, database, schema)
        # need row count if using local files (since sampling is done live from the file)

    else:
        raise NotImplementedError(
            f"Connector type {type(pr.connector)} is not yet supported"
        )

    # need row count if using local files (since sampling is done live from the file)
    if isinstance(pr.connector, _FileConnector):
        if isinstance(pr.connector, DatabaseFileConnector):
            # in this case, location is not the real path, but the database and schema, but we can use the path from the connector
            path = os.path.relpath(pr.connector._path, root_path)
        else:
            path = os.path.relpath(source._location, root_path)
        out["config"]["path"] = path
        if not pr.connector._remote and twin:
            try:
                count = tbl.count().execute()
                # in this case, we will not be caching the table, so we need the row_count
            except Exception:
                try:
                    # try to count the first column
                    first_col = tbl.columns[0]
                    count = tbl.aggregate(tbl[first_col].count()).execute().iloc[0, 0]
                except Exception:
                    # if we can't get the row count, we will just use a small default value, so we get a full sample
                    count = 0.01
            out["config"]["row_count"] = count

    if source._schema is None:
        raise ValueError(f"Schema for {source._name} is not available")

    out["config"]["columns"] = {}
    prev_replacements: list[str] = []
    col_replace_dict = {}
    for col_name, col_type in source._schema.items():
        if not is_valid_class_name(col_name):
            old_col_name = col_name
            col_name = to_valid_class_name(old_col_name, prev_replacements)
            prev_replacements.append(col_name)
            col_replace_dict[col_name] = old_col_name
        if col_name in saved_attributes:
            out["config"]["columns"][col_name] = saved_attributes[col_name]
        else:
            out["config"]["columns"][col_name] = {}

        out["config"]["columns"][col_name] = {"type": str(col_type)}

    out["config"]["col_replace"] = col_replace_dict
    return out


def _get_save_dir(sources_path: str, source: SourceInfo) -> str:
    if source._parent_resource is None:
        raise ValueError("Source must have a parent resource.")
    if isinstance(source._parent_resource.connector, _TableConnector):
        # source is a file
        return os.path.join(sources_path, source._parent_resource.name)
    if isinstance(source._parent_resource.connector, _DatabaseConnector):
        # source is a database
        identifers = [
            _make_python_identifier(str_) for str_ in source._location.split(".")
        ]
        return os.path.join(sources_path, source._parent_resource.name, *identifers)
    raise NotImplementedError(
        f"Connector type {type(source._parent_resource.connector)} is not yet supported"
    )


def generate_sources_helper(
    resources=[],
    additional_saved_attributes: dict[str, dict[str, Any]] = {},
    json: bool = False,
    defs=None,
    twin: bool = False,
) -> tuple[list[SourceInfo], list[dict[str, Any]]]:
    if defs is None:
        defs = _load_project_defs()
    if len(resources) == 0:
        project = Project(resources=defs.resources)
    else:
        project = Project(
            resources=[r for r in defs.resources if r.__name__ in resources]
        )

    sources, errors = project._get_source_objects(with_schema=True)

    if not json:
        root_file = _load_project_module().__file__
        if root_file is None:
            raise ValueError("Unable to find the module path for the current project")
        root_path = os.path.dirname(root_file)
        sources_path = os.path.join(root_path, "sources")

        _create_dirs_with_init_py(sources_path)

    source_list = []

    for source in tqdm(
        sources,
        desc="generating source files" if not json else "generating source dicts",
    ):
        if not json:
            save_dir = _get_save_dir(sources_path, source)
            file_path = os.path.join(save_dir, f"{source._name}.py")
            _create_dirs_with_init_py(save_dir)

            try:
                saved_attributes = _find_classes_and_attributes(file_path)
            except (IndexError, FileNotFoundError):
                saved_attributes = {}

            try:
                saved_attributes.update(
                    additional_saved_attributes[source._parent_resource.name][
                        table_to_python_class(source._name)
                    ]
                )
            except KeyError:
                pass

        if json:
            source_data = source_to_class_dict(
                source, {}, root_path="tenant", twin=twin
            )
            source_list.append(source_data)
            continue

        saved_imports = (
            _get_imports_from_file_regex(file_path)
            if saved_attributes != {} and os.path.exists(file_path)
            else None
        )
        with open(os.path.join(save_dir, f"{source._name}.py"), "w+") as f:
            out = ""
            if saved_imports:
                out += saved_imports
            else:
                out += "# type: ignore\n"  # prevents pylance errors tied to Ibis
                out += "from vinyl import Field, source # noqa F401\n"
                out += "from vinyl import types as t # noqa F401\n"
                out += "from ibis.common.collections import FrozenDict # noqa F401\n\n"
                out += f"from {source._parent_resource.def_.__module__} import {source._parent_resource.def_.__name__} # noqa F401 \n\n\n"
            out += f"@source(resource={source._parent_resource.name})\n"
            out += source_to_class_string(
                source, saved_attributes, root_path=root_path, twin=twin
            )
            try:
                out = ruff_format_text(out)
            except Exception as e:
                print(f"Error formatting {source._name}: {e}")
            f.write(out)
    return sources, source_list, errors


@sources_cli.command("generate")
def generate_sources(
    twin: bool = typer.Option(
        False, "--generate_twin", "-t", help="exported name of the model"
    ),
    resources: list[str] = typer.Option(
        [], "--resource", "-r", help="resource names to select"
    ),
    json: bool = typer.Option(
        False, "--json", "-j", help="output as json instead of in directory"
    ),
):
    """Generates schema files for sources"""
    # track = EventLogger()
    # track.log_event(Event.SOURCE_GEN)
    root_file = _load_project_module().__file__
    if root_file is None:
        raise ValueError("Unable to find the module path for the current project")
    root_path = os.path.dirname(root_file)
    sources_path = os.path.join(root_path, "sources")

    @_with_modified_env("NO_MODELS_VINYL", "True")
    def run_fn():
        sources, _, _ = generate_sources_helper(resources, json=json, twin=twin)

        if twin:
            msg = "generating twins... " if len(sources) > 1 else "generating twin... "
            for source in tqdm(
                sources,
                msg,
                unit="source",
            ):
                pr = source._parent_resource
                if isinstance(pr.connector, _DatabaseConnector):
                    database, schema = source._location.split(".")
                    pr.connector._generate_twin(
                        os.path.join(root_path, _get_twin_relative_path(pr.name)),
                        database,
                        schema,
                        source.name,
                    )
                elif isinstance(pr.connector, _TableConnector):
                    # doesn't actually generate a file, just returns the path
                    pr.connector._generate_twin(source.location)

        print(f"Generated {len(sources)} sources at {sources_path}")

    run_fn()
