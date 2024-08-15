from __future__ import annotations

import ast
import os
from typing import Any

from app.core.db_methods import (
    dbt_repo_context,
)
from dotenv import load_dotenv
from supabase import Client
from vinyl.cli.dbt import (
    DBTProjectStructure,
    generate_models_helper,
    generate_resources_helper,
)
from vinyl.cli.sources import generate_sources_helper
from vinyl.lib.dbt import DBTDialect
from vinyl.lib.dbt_methods import DBTVersion
from vinyl.lib.definitions import Defs, _create_dag_from_model_dict_list  # noqa
from vinyl.lib.project import Project

from backend.core.serialization import (  # noqa
    ModelObject,
    ResourceObject,
    SourceObject,
)

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


def undo_insertion_on_error(func):
    def wrapper(self: VinylDB, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.undo_insertion_on_error_helper()
            self.errors_cleaned = True
            raise e

    return wrapper


class VinylDB:
    def __init__(self, supabase_client: Client, tenant_id: str | None = None):
        self.supabase_client = supabase_client
        self.tenant_id = tenant_id
        self.resource_id_dict = {}
        self.asset_id_dict = {}
        self.asset_link_id_dict = {}
        self.column_id_dict = {}
        self.column_link_id_dict = {}
        self.resource_id_dict = {}
        self.errors_cleaned = (
            False  # ensures that errors are only cleaned once even for nested calls
        )

    @undo_insertion_on_error
    def setup_dbt_project(
        self,
        tenant_id: str,
        repo_id: str,
        dialect: DBTDialect,
        version: DBTVersion,
        gen_models: bool = False,
    ):
        with dbt_repo_context(
            self.supabase_client, repo_id, tenant_id, dialect=dialect, version=version
        ) as dbtproj:
            res = generate_resources_helper(dbtproj, json_=True)
            res["repository_id"] = repo_id
            out = {}
            data, count = self.supabase_client.table("resources").insert(res).execute()
            out["resources"] = self.update_resources_data(data[-1])
            self.resource_id_dict = {v["name"]: v["id"] for v in out["resources"]}
            if gen_models:
                models, asset_links = generate_models_helper(
                    dbtproj,
                    structure=DBTProjectStructure.JSON,
                )
                out["models"] = models
                out["asset_links"] = asset_links

            return out

    def undo_insertion_on_error_helper(self):
        dict_map = {
            "column_links": self.column_link_id_dict,
            "columns": self.column_id_dict,
            "asset_links": self.asset_link_id_dict,
            "assets": self.asset_id_dict,
            "resources": self.resource_id_dict,
        }  # order of dict map is made to minimize fk constraint error risk
        for k, v in dict_map.items():
            if len(v) > 0 and not self.errors_cleaned:
                data, count = (
                    self.supabase_client.table(k)
                    .delete()
                    .in_("id", [v for v in v.values()])
                    .execute()
                )

    def update_resources_data(self, resources_data):
        for v in resources_data:
            # make sure input is a list not a jsonified string
            if isinstance(v["tables"], str):
                v["tables"] = ast.literal_eval(v["tables"])
            v["supabase_url"] = self.url
            v["supabase_key"] = self.key
        return resources_data

    @undo_insertion_on_error
    def generate_sources(self, resource_ids: list[str]):
        defs_dict = {}
        data, count = (
            self.supabase_client.table("resources")
            .select("*")
            .in_("id", resource_ids)
            .execute()
        )
        resources_data = self.update_resources_data(data[-1])
        self.resource_id_dict = {v["name"]: v["id"] for v in resources_data}

        defs_dict["resources"] = resources_data

        defs = Defs.load_from_dict(defs_dict)

        sources, source_json = generate_sources_helper(json=True, defs=defs, twin=False)
        for v in source_json:
            v["resource_ids"] = [self.resource_id_dict[v["resource_name"]]]
        return source_json

    @undo_insertion_on_error
    def ingest_dbt_project(
        self, repo_id: str, tenant_id: str, dialect: DBTDialect, version: DBTVersion
    ):
        dbt_proj_info = self.setup_dbt_project(
            repo_id, dialect, tenant_id, version, gen_models=True
        )
        sources = self.generate_sources([v["id"] for v in dbt_proj_info["resources"]])
        model_dag = _create_dag_from_model_dict_list(dbt_proj_info["models"])
        for model in dbt_proj_info["models"]:
            ancestor_roots = model_dag.get_ancestor_roots([model["unique_name"]])
            source_ancestor_roots = [n for n in ancestor_roots if ".sources." in n]
            resource_ids = []
            for v in sources:
                if v["unique_name"] in source_ancestor_roots:
                    resource_ids.append(self.resource_id_dict[v["resource_name"]])

            # handle sql models where model may not be connected to a source
            if resource_ids == []:
                res_name = model["config"]["steps"][0].get("resource_name", None)
                if res_name is not None:
                    resource_ids.append(self.resource_id_dict[res_name])
            model["resource_ids"] = list(set(resource_ids))
        for source in sources:
            del source["resource_name"]  # no longer needed

        defs_dict = {
            "resources": dbt_proj_info["resources"],
            "sources": sources,
            "models": dbt_proj_info["models"],
        }
        self.upload_assets(defs_dict, dbt_proj_info["asset_links"])
        return Project.bootstrap_from_dict(defs_dict)

    @undo_insertion_on_error
    def upload_assets(
        self, defs_dict: dict[str, Any], asset_links: list[dict[str, str]]
    ):
        assets_to_upload = [
            SourceObject(**i).model_dump()  # type: ignore[attr-defined]
            for i in defs_dict["sources"]
        ]
        assets_to_upload += [ModelObject(**i).model_dump() for i in defs_dict["models"]]  # type: ignore[attr-defined]
        data, count = (
            self.supabase_client.table("assets").insert(assets_to_upload).execute()
        )
        self.asset_id_dict = {v["unique_name"]: v["id"] for v in data[1]}
        adj_asset_links = []
        for link in asset_links:
            adj_asset_links.append(
                {
                    "type": link["type"],
                    "source_id": self.asset_id_dict[link["source_unique_name"]],
                    "target_id": self.asset_id_dict[link["target_unique_name"]],
                }
            )
        data, count = (
            self.supabase_client.table("asset_links").insert(adj_asset_links).execute()
        )
        self.asset_link_id_dict = {v["source_id"]: v["id"] for v in data[1]}
        return data[-1]

    @undo_insertion_on_error
    def upload_columns(
        self,
        resource_ids: list[str] | None = None,
        ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
    ):
        project = self.get_project(resource_ids)
        sqlproject = project.get_sql_project(
            parallel=False,
            ids=ids,
            predecessor_depth=predecessor_depth,
            successor_depth=successor_depth,
        )
        sqlproject.optimize()
        columns, column_links = sqlproject.stitch_lineage_postgres()
        assets_data = self.get_assets_data(resource_ids)
        if self.asset_id_dict == {}:
            if resource_ids is None:
                raise ValueError(
                    "resource_ids must be provided if asset_id_dict is empty"
                )
            # in case running as a standalone function, get correct assets but dont update asset_id_dict
            asset_id_dict = {v["unique_name"]: v["id"] for v in assets_data}
        else:
            asset_id_dict = self.asset_id_dict
        for col in columns:
            col["asset_id"] = asset_id_dict.get(col["table_unique_name"], None)
            if "errors" in col and col["errors"] != []:
                col["errors"] = [err.to_dict() for err in col["errors"]]
            if col["asset_id"] is not None:
                asset_it = [v for v in assets_data if v["id"] == col["asset_id"]][0]
                col["description"] = (
                    asset_it["config"]
                    .get("column_descriptions", {})
                    .get(col["name"], None)
                )
        data, count = self.supabase_client.table("columns").insert(columns).execute()
        self.column_id_dict = {
            f"{v['table_unique_name']}.{v['name']}": v["id"] for v in data[1]
        }
        adj_column_links = []
        for link in column_links:
            adj_column_links.append(
                {
                    "lineage_type": link["lineage_type"],
                    "connection_types": link["connection_types"],
                    "source_id": self.column_id_dict[link["source_name"]],
                    "target_id": self.column_id_dict[link["target_name"]],
                }
            )
        data, count = (
            self.supabase_client.table("column_links")
            .insert(adj_column_links)
            .execute()
        )
        self.column_link_id_dict = {v["source_id"]: v["id"] for v in data[1]}

    def get_resources_data(
        self, repo_ids: list[str] = [], additional_resources: list[str] = []
    ):
        builder = self.supabase_client.table("resources")
        query = "id, name, type, tables, config, profiles(encrypted_secret)"
        if repo_ids:
            query += ", repositories(id, tables, repo_path_zip)"
        builder = builder.select(query)
        if repo_ids and additional_resources:
            repo_id_string = ", ".join(repo_ids)
            resource_id_string = ", ".join(additional_resources)
            builder = builder.or_(
                f"repositories.id.in.{repo_id_string}",
                f"id.in.{resource_id_string}",
            )
        elif repo_ids:
            builder = builder.in_("repositories.id", repo_ids)
        elif additional_resources:
            builder = builder.in_("id", additional_resources)
        else:
            raise ValueError("Must provide either repo_ids or additional_resources")

        if self.tenant_id is not None:
            builder.eq("tenant_id", self.tenant_id)

        data, count = builder.execute()
        resources = data[-1]
        for res in resources:
            repositories = res.get("repositories", None)
            if repositories is not None:
                if len(repositories) > 1:
                    raise ValueError(
                        "Multiple repositories found for a resource after filtering"
                    )
                if len(repositories) == 1:
                    res["repositories"] = repositories[-1]

        return resources

        # rename resource fields to be compatible with ResourceObject
        # for res in resources:
        #     if "repositories" in res:
        #         res["repository_config"] = res.pop("repositories")
        #     if "profiles" in res:
        #         res["profiles_config"] = res.pop("profiles")

        return resources

    def get_assets_data(self, resource_ids: list[str] | None = None):
        # get sources
        builder = self.supabase_client.table("assets").select("*")
        if resource_ids is None:
            builder = builder.is_("resource_ids", "null")
        else:
            stringified = "{"
            for i, v in enumerate(resource_ids):
                stringified += f'"{v}"'
                if i != len(resource_ids) - 1:
                    stringified += ","
            stringified += "}"
            builder = builder.filter("resource_ids", "cs", stringified)
        data, count = builder.execute()

        return data[-1]

    def get_defs_dict(self, resource_ids: list[str] | None = None):
        resources_data = self.get_resources_data(resource_ids)
        for v in resources_data:
            v["supabase_url"] = self.url
            v["supabase_key"] = self.key
        assets_data = self.get_assets_data(resource_ids)
        models_data = [v for v in assets_data if v["type"] == "model"]
        sources_data = [v for v in assets_data if v["type"] == "source"]
        return {
            "resources": resources_data,
            "sources": sources_data,
            "models": models_data,
        }

    def get_project(self, resource_ids: list[str] | None = None):
        defs_dict = self.get_defs_dict(resource_ids)
        return Project.bootstrap_from_dict(defs_dict)

    def get_related_assets(
        self,
        asset_ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
    ):
        successor_data, count = self.supabase_client.rpc(
            "assets_bfs",
            {
                "nodes": asset_ids,
                "max_depth": successor_depth,
            },
        ).execute()
        predecessor_data, count = self.supabase_client.rpc(
            "assets_bfs_inverse",
            {
                "nodes": asset_ids,
                "max_depth": predecessor_depth,
            },
        ).execute()

        asset_ids.extend([v["node_id"] for v in predecessor_data[1]])
        asset_ids.extend([v["node_id"] for v in successor_data[1]])
        return asset_ids

    async def get_lineage(
        self,
        asset_id: str,
    ):
        column_data, count = (
            self.supabase_client.table("columns")
            .select("*")
            .in_("asset_id", asset_id)
            .execute()
        )
        column_ids = [v["id"] for v in column_data[-1]]
        column_links_data, count = (
            self.supabase_cliendt.table("column_links")
            .select("*")
            .in_("target_id", column_ids)
            .execute()
        )
        return column_data[-1], column_links_data[-1]

    def clean_db(self):
        for tbl in ["resources", "assets", "columns", "column_links", "asset_links"]:
            self.supabase_client.table(tbl).delete().filter(
                "id", "not.is", "null"
            ).execute()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    from datastore import supabase

    db = VinylDB(supabase_client=supabase)
    # x = db.upload_columns(
    #     resource_ids=["46045b81-829d-4698-a280-b87a6e708814"],
    #     ids=["stg_posthog__events"],
    # )
    y = db.get_resources_data(repo_ids=["b7b5d42e-6558-410c-ac7b-c8e116a6c802"])[0]
    from backend.core.serialization import ResourceObject

    yy = ResourceObject(**y)
    yy._get_connector()._connect()
    # breakpoint()
    # x = get_dbt_profile_contents_from_resource(data[1])
    # import os
    # from base64 import urlsafe_b64decode

    # from cryptography.fernet import Fernet
    # from dotenv import load_dotenv

    # load_dotenv()

    # ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    # cipher = Fernet(ENCRYPTION_KEY)

    # decrypted_secret = cipher.decrypt(urlsafe_b64decode(secret)).decode("utf-8")
    breakpoint()
    # db.clean_db()
    # proj = db.ingest_dbt_project(
    #     "8200dcbe-0641-4a66-9091-ce7482319603", DBTDialect.BIGQUERY, DBTVersion.V1_5
    # )
    # print(db.get_assets_data(resource_ids=["0e30d4e2-76c4-4538-967c-0491551e1452"]))
    # db.upload_columns(
    #     resource_ids=["46045b81-829d-4698-a280-b87a6e708814"],
    #     # ids=["internal_project.models.dbt.base_posthog__users"],
    # )
