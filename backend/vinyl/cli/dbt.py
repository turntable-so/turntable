import json
import os
from enum import Enum
from typing import Any

import typer
from bidict import bidict

from vinyl.lib.dbt import DBTProject
from vinyl.lib.dbt_methods import DBTDialect, DBTVersion
from vinyl.lib.settings import _get_project_module_name
from vinyl.lib.utils.files import ruff_format_text
from vinyl.lib.utils.obj import (
    table_to_python_class,
)
from vinyl.lib.utils.text import (
    _escape_triple_quotes,
    _generate_random_ascii_string,
    _make_python_identifier,
    _replace_with_dict,
)

dbt_cli: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)
dbt_cli_resources: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)
dbt_cli_models: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)

dbt_cli.add_typer(dbt_cli_resources, name="resources")
dbt_cli.add_typer(dbt_cli_models, name="models")


def get_dbt_resource_name(dbtproj):
    project_name = dbtproj.dbt_project_yml["name"]
    return f"dbt_{project_name}"


def get_source_relation_names(
    dbtproj: DBTProject,
    resource_name_override: str | None = None,
) -> tuple[list[str], list[str | None], dict[tuple[str, str], str | None]]:
    vinyl_addresses = []
    db_addresses = []
    vinyl_source_path_dict = {}
    dbtproj.mount_manifest()
    for source in dbtproj.manifest["sources"].values():
        unadorned_relation_name = (
            f'{source["database"]}.{source["schema"]}.{source["name"]}'
        )
        vinyl_addresses.append(unadorned_relation_name)
        relation_name = dbtproj.get_relation_name(source["unique_id"])
        db_addresses.append(relation_name)
        source_module_name = _get_project_module_name() + ".sources."
        if resource_name_override is not None:
            source_module_name += resource_name_override
        else:
            source_module_name += get_dbt_resource_name(dbtproj)
        for key in ["database", "schema", "name"]:
            source_module_name += f".{source[key]}"
        vinyl_source_path_dict[
            (
                ".".join(
                    [_make_python_identifier(i) for i in source_module_name.split(".")]
                ),
                table_to_python_class(source["name"]),
            )
        ] = relation_name
    return vinyl_addresses, db_addresses, vinyl_source_path_dict


def generate_resources_helper(
    dbtproj: DBTProject, json_: bool = False, resource_name_override: str | None = None
):
    dialect = dbtproj.dialect
    version = dbtproj.version
    dbt_project_dir = dbtproj.dbt_project_dir
    vinyl_addresses, _, _ = get_source_relation_names(dbtproj)
    resource_name = (
        resource_name_override
        if resource_name_override
        else get_dbt_resource_name(dbtproj)
    )
    if json_:
        return {
            "name": resource_name,
            "type": "DBT",
            "tables": vinyl_addresses,
            "config": {
                "dialect": dialect.name,
                "version": version.name,
            },
        }
    additional_imports = """

from vinyl.lib.asset import resource
from vinyl.lib.connect import DBTConnectorFull
from vinyl.lib.dbt_methods import DBTDialect, DBTVersion

"""
    additional_resources = f"""
    
@resource
def {resource_name}():
    return DBTConnectorFull(dbt_project_dir = "{dbt_project_dir}", dialect = {str(dialect)}, version = {str(version)}, tables = {json.dumps(vinyl_addresses)})
"""
    # update resources.py
    resources_path = f"{_get_project_module_name()}/resources.py"
    if os.path.exists(resources_path):
        with open(resources_path, "r") as f:
            cur_contents = f.read()
        contents_split = cur_contents.split("@resource")
        contents_split = [
            x
            for x in contents_split
            if not x.strip().startswith(f"def {get_dbt_resource_name(dbtproj)}():")
        ]
        contents_split[0] += (
            additional_imports  # add new imports to the imports of the original
        )
    else:
        contents_split = [additional_imports]

    new_contents = "@resource".join(contents_split) + additional_resources
    new_contents = ruff_format_text(new_contents)

    with open(resources_path, "w") as f:
        f.write(new_contents)


@dbt_cli_resources.command("generate")
def generate_resources(
    dbt_project_dir: str = typer.Option(
        None, "--root", "-r", help="path to dbt project root"
    ),
    dialect: DBTDialect = typer.Option(
        None,
        "--dialect",
        "-d",
        help="dialect of dbt project. Snowflake, Bigquery, Postgres, and DuckDB supported.",
    ),
    version: DBTVersion = typer.Option(
        "1.7", "--version", "-v", help="dbt major version. 1.3-1.7 supported"
    ),
    json_: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="if true, output will be in json format",
    ),
):
    dbtproj = DBTProject(dbt_project_dir, dialect, version, manifest_req=True)
    return generate_resources_helper(dbtproj, json_)


class DBTProjectStructure(Enum):
    ONE_FILE = "one_file"
    DBT_like = "dbt_like"
    JSON = "json"


def generate_models_helper(
    dbtproj: DBTProject,
    structure: DBTProjectStructure,
    proj_name: str = "proj",
    resource_name_override: str | None = None,
    repository_id: str | None = None,
    descriptions: bool = True,
):
    dbtproj.mount_manifest()
    dbtproj.build_model_graph(include_sources=True)
    dbt_models = dbtproj.manifest["nodes"]
    if not os.path.exists(dbtproj.compiled_sql_path):
        dbtproj.dbt_compile(models_only=True)
    _, _, vinyl_source_path_dict = get_source_relation_names(
        dbtproj, resource_name_override
    )
    vinyl_source_path_dict_bd: bidict[tuple[str, str], str] = bidict(
        {
            k: v
            for k, v in vinyl_source_path_dict.items()
            if v is not None and k[0] is not None and k[1] is not None
        }
    )
    find_replace: bidict[str, str] = bidict(
        {v: k[0] for k, v in vinyl_source_path_dict.items() if v is not None}
    )
    find_replace_models = {
        dbtproj.get_relation_name(n): n
        for n in dbtproj.model_graph.node_dict
        if n.startswith("model.")
    }
    find_replace.update({k: v for k, v in find_replace_models.items() if k is not None})
    sorted = dbtproj.model_graph.topological_sort()

    if structure != DBTProjectStructure.JSON:
        out_str = "from vinyl import VinylTable, model\n"
        out_str += "from vinyl.lib.asset import get_resource_by_name\n"
        for k, v in vinyl_source_path_dict.items():
            out_str += f"from {k[0]} import {k[1]}\n"
        out_str += "\n"
    else:
        out_ls = []
    asset_links = []
    errors = []
    for node in sorted:
        if not node.startswith("model."):
            continue
        parents = dbtproj.model_graph.get_relatives(
            [node], depth=1, reverse=True, include_sources=False
        )

        # build loookup translating vinyl class / function names to db relation_names
        parent_vinyl_names: dict[str, str] = {}
        for parent in parents:
            if not parent.startswith("source.") and parent in find_replace.inv:
                split_ = parent.split(".")[-1] or parent
                parent_vinyl_names[split_] = find_replace.inv[parent]
            else:
                rel_name = dbtproj.get_relation_name(parent)
                if rel_name is not None:
                    adj_name = vinyl_source_path_dict_bd.inv.get(
                        rel_name, [None, None]
                    )[1]
                    if adj_name is not None:
                        parent_vinyl_names[adj_name] = rel_name
        deps = ", ".join([k for k in parent_vinyl_names.keys()])
        if descriptions:
            description = dbt_models[node].get("description", None)
        else:
            description = None
        destination = [
            dbt_models[node].get(attr) for attr in ["database", "schema", "name"]
        ]
        tags = dbt_models[node]["config"].get("tags", None)
        if dbt_models[node].get("columns", {}) == {} or not descriptions:
            column_descriptions = None
        else:
            column_descriptions = {
                col_name: col.get("description")
                for col_name, col in dbt_models[node]["columns"].items()
            }

        if structure != DBTProjectStructure.JSON:
            model_string = f"@model(deps=[{deps}]"
            if description is not None:
                model_string += (
                    f", description='''{_escape_triple_quotes(description)}'''"
                )
            if tags is not None:
                tags_string = ", ".join(f"'{tag}'" for tag in tags)
                model_string += f", tags=[{tags_string}]"
            if column_descriptions is not None:
                column_descriptions_string = ", ".join(
                    f"'{k}': '''{_escape_triple_quotes(v)}'''"
                    for k, v in column_descriptions.items()
                )
                model_string += (
                    f", column_descriptions={{{column_descriptions_string}}}"
                )
            model_string += ")\n"
        else:
            model_list: dict[str, Any] = {
                "type": "model",
                "config": {},
            }
            model_list["read_only"] = True
            model_list["config"]["publish"] = False
            if description is not None:
                # top level attribute... not in config dict
                model_list["description"] = description
            if destination is not None:
                model_list["config"]["destination"] = destination
            if tags is not None:
                model_list["config"]["tags"] = tags
            if column_descriptions is not None:
                model_list["config"]["column_descriptions"] = column_descriptions

        # build compiled sql and sources with shortened names
        parent_vinyl_names_shortened: bidict[str, str] = bidict({})
        parent_vinyl_names_shortened_and_randomized: bidict[str, str] = bidict({})
        letters_count: dict[str, int] = {}
        for name, v in parent_vinyl_names.items():
            single_char = name[0].lower()
            letter_count_it = letters_count.get(single_char, 0)
            shortened = (
                single_char + str(letter_count_it)
                if letter_count_it > 0
                else single_char
            )
            letters_count[single_char] = letter_count_it + 1
            parent_vinyl_names_shortened[shortened] = v
            shortened_random = f"{shortened}_{_generate_random_ascii_string(6)}"
            parent_vinyl_names_shortened_and_randomized[shortened_random] = v

        if structure != DBTProjectStructure.JSON:
            argsx = ", ".join(parent_vinyl_names_shortened.keys())

            # create function
            model_string += f"def {node.split('.')[-1]}({argsx}):\n"

            # build source string
            source_string_list = []
            for k2, v2 in parent_vinyl_names_shortened.items():
                source_string_list.append(
                    f'"{parent_vinyl_names_shortened_and_randomized.inv[v2]}": {k2}'
                )  # use random string name to avoid cte alias conflicts in sql
            source_string = "{" + ", ".join(source_string_list) + "}"
        else:
            model_list["name"] = node.split(".")[-1]
            model_list["unique_name"] = f"{proj_name}.models.dbt.{model_list['name']}"
            model_list["config"]["deps"] = {}
            for k, v in parent_vinyl_names_shortened.items():
                if not find_replace[v].startswith("model."):
                    rest, name = find_replace[v].rsplit(".", 1)
                    name = table_to_python_class(name)
                    new_v = f"{rest}.{name}"
                else:
                    new_v = (
                        f"{proj_name}.models.dbt.{find_replace[v].rsplit('.',1)[-1]}"
                    )
                    # this is imperfect, but ensures that the class name is valid
                asset_links.append(
                    {
                        "type": "db",
                        "source_unique_name": new_v,
                        "target_unique_name": model_list["unique_name"],
                    }
                )
                model_list["config"]["deps"][k] = new_v

            sql_step = {
                "type": "SQL",
                "sources": {
                    parent_vinyl_names_shortened_and_randomized.inv[v2]: k2
                    for k2, v2 in parent_vinyl_names_shortened.items()
                },
                "destination": destination,
                "output": "0",
            }
            if sql_step["sources"] == {}:
                sql_step["repository_id"] = repository_id

            model_list["config"]["steps"] = [
                sql_step,
                {"type": "Return", "input": "0"},
            ]

        # retrieve and adjust compiled_sql
        compiled_sql, errors_it = dbtproj.get_compiled_sql(
            node, errors=[], compile_if_not_found=False
        )  # save errors to errors_it, already compiled so don't try to compile if can't find
        if errors_it != []:
            for err in errors_it:
                err.node_id = node
            errors.extend(errors_it)
        else:
            compiled_sql = _replace_with_dict(
                compiled_sql, parent_vinyl_names_shortened_and_randomized.inv
            )
        if structure != DBTProjectStructure.JSON:
            model_string += f"""    sql = '''
    {_escape_triple_quotes(compiled_sql)}
    '''\n"""
            if source_string == "{}":
                model_string += (
                    f"    return VinylTable.from_sql(sql, sources={source_string}, resource = get_resource_by_name('{get_dbt_resource_name(dbtproj)}')"
                    ""
                )
            else:
                model_string += (
                    f"    return VinylTable.from_sql(sql, sources={source_string}" ""
                )
            if destination is not None:
                destination_string = ", ".join(
                    f'"{dest}"' if dest is not None else dest for dest in destination
                )
                model_string += f", destination=[{destination_string}]"
            model_string += ")\n\n"
            out_str += model_string
        else:
            model_list["config"]["steps"][0]["sql"] = compiled_sql
            out_ls.append(model_list)

    if structure == DBTProjectStructure.JSON:
        return out_ls, asset_links, errors
    else:
        out_str = ruff_format_text(out_str)

        with open(f"{_get_project_module_name()}/models/dbt.py", "w") as f:
            f.write(out_str)
        return out_str, None, errors


@dbt_cli_models.command("generate")
def generate_models(
    dbt_project_dir: str = typer.Option(
        None, "--root", "-r", help="path to dbt project root"
    ),
    dialect: DBTDialect = typer.Option(
        None,
        "--dialect",
        "-d",
        help="dialect of dbt project. Snowflake, Bigquery, Postgres, and DuckDB supported.",
    ),
    version: DBTVersion = typer.Option(
        "1.7", "--version", "-v", help="dbt major version. 1.3-1.7 supported"
    ),
    structure: DBTProjectStructure = typer.Option(
        "one_file", "--structure", "-s", help="structure of the generated models"
    ),
    no_descriptions: bool = typer.Option(
        False,
        "--no-descriptions",
        "-desc",
        is_flag=True,
        help="if true, descriptions will be included in the generated models",
    ),
):
    dbtproj = DBTProject(dbt_project_dir, dialect, version, manifest_req=True)
    return generate_models_helper(dbtproj, structure, descriptions=not no_descriptions)


if __name__ == "__main__":
    x = generate_models(
        "../../turntable_dbt",
        DBTDialect.BIGQUERY,
        DBTVersion.V1_5,
        DBTProjectStructure.JSON,
    )[0]
    y = [
        i
        for i in x
        if i["unique_name"]
        == "internal_project.models.dbt.dbt_metrics_default_calendar"
    ][0]
