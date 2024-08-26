from __future__ import annotations

import copy
import os
import traceback
from typing import Any, Callable, Literal

import django
import duckdb
import ibis
import networkx as nx
import orjson
import sqlglot
from datahub.metadata.com.linkedin.pegasus2avro.assertion import (
    DatasetAssertionScope,
)
from datahub.metadata.urns import ChartUrn, DashboardUrn, DatasetUrn, SchemaFieldUrn
from datahub.utilities.urns.error import InvalidUrnError
from django.forms.models import model_to_dict
from sqlglot import Expression, exp
from sqlglot.errors import ParseError

from app.models import Asset, Resource, ResourceType
from app.utils.database import delete_and_upsert
from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.schema import VinylSchema
from vinyl.lib.sqlast import SQLAstNode
from vinyl.lib.utils.graph import nx_remove_node_and_reconnect

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

from app.models import AssetError, AssetLink, Column, ColumnLink

_STR_JOIN_HELPER = "_____"


def get_duplicate_nodes_key(asset_id: str):
    if asset_id.startswith("urn:li:dataset:"):
        parsed_ds = DatasetUrn.from_string(asset_id)
        key = parsed_ds.name
    elif asset_id.startswith("urn:li:schemaField:"):
        parsed_sf = SchemaFieldUrn.from_string(asset_id)
        parsed_ds = DatasetUrn.from_string(parsed_sf.parent)
        key = f"{parsed_ds.name}.{parsed_sf.field_path}"
    else:
        key = asset_id
        parsed_ds = None

    return key, parsed_ds


def base_prioritization_f(id: str) -> bool:
    key, parsed_ds = get_duplicate_nodes_key(id)
    if parsed_ds is None:
        return None
    elif parsed_ds.platform != "urn:li:dataPlatform:dbt":
        # use dbt by default
        return True
    else:
        return False


def get_duplicate_nodes_helper(
    ids: list[str], segmentation_f: Callable[[str], bool | None]
):
    duplicate_helper = {}
    for id in ids:
        key, parsed_ds = get_duplicate_nodes_key(id)
        pri = segmentation_f(id)
        if pri is None:
            continue
        elif pri:
            duplicate_helper.setdefault(key, []).insert(0, id)
        else:
            duplicate_helper.setdefault(key, []).append(id)

    return duplicate_helper


class DataHubDBParserBase:
    def __init__(
        self,
        row_dict: dict[str, dict[str, Any]] = {},
        asset_dict: dict[str, Asset] = {},
        column_dict: dict[str, Column] = {},
        asset_graph: nx.DiGraph = nx.DiGraph(),
        column_graph: nx.MultiDiGraph = nx.MultiDiGraph(),
        is_db: bool = False,
        dialect: str = "postgres",
    ):
        self.row_dict = row_dict
        self.asset_dict = asset_dict
        self.column_dict = column_dict
        self.asset_graph = asset_graph
        self.column_graph = column_graph
        self.is_db = is_db
        self.dialect = dialect

    def parse(self):
        pass

    def get_config(self, id: str):
        if id not in self.asset_dict:
            raise ValueError(f"{id} not in asset_dict")
        if self.asset_dict[id].config is None:
            self.asset_dict[id].config = {}
        return self.asset_dict[id].config

    def get_outputs(self):
        return {
            "row_dict": self.row_dict,
            "asset_dict": self.asset_dict,
            "column_dict": self.column_dict,
            "asset_graph": self.asset_graph,
            "column_graph": self.column_graph,
            "is_db": self.is_db,
            "dialect": self.dialect,
        }

    def assets_as_dict(self):
        for asset in self.asset_dict.values():
            yield model_to_dict(asset)


# order of these parsers is important, do not reorder.
class OwnershipParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.row_dict.items():
            if "ownership" in v and k in self.asset_dict:
                for info in v["ownership"]:
                    owners = {
                        str(o["owner"]).replace("urn:li:corpuser:", "")
                        for o in info["owners"]
                    }
                    config = self.get_config(k)
                    config.setdefault("owners", []).extend(owners)
                    config["owners"] = list(set(self.asset_dict[k].config["owners"]))


class ViewsParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.row_dict.items():
            if "chartUsageStatistics" in v and k in self.asset_dict:
                for stats in v["chartUsageStatistics"]:
                    config = self.get_config(k)
                    config["views"] = stats["viewsCount"]
            elif "dashboardUsageStatistics" in v:
                for stats in v["dashboardUsageStatistics"]:
                    config = self.get_config(k)
                    config["views"] = stats["viewsCount"]


class ChartInfoParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.row_dict.items():
            if "chartInfo" in v and k in self.asset_dict:
                for info in v["chartInfo"]:
                    self.asset_dict[k].name = info["title"]
                    if "description" in info:
                        self.asset_dict[k].description = info["description"]
                    if "chartUrl" in info:
                        config = self.get_config(k)
                        config["url"] = info["chartUrl"]
                    if "inputs" in info:
                        for input in info["inputs"]:
                            self.asset_graph.add_edge(input["string"], k)

        # add name if there's no title
        for k, v in self.asset_dict.items():
            if not v.name and "urn:li:chart:" in k:
                parsed = ChartUrn.from_string(k)
                v.name = parsed.chart_id


class DashboardInfoParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.row_dict.items():
            if "dashboardInfo" in v and k in self.asset_dict:
                for info in v["dashboardInfo"]:
                    self.asset_dict[k].name = info["title"]
                    if "description" in info:
                        self.asset_dict[k].description = info["description"]
                    if "dashboardUrl" in info:
                        config = self.get_config(k)
                        config["url"] = info["dashboardUrl"]
                    if "charts" in info:
                        for chart in info["charts"]:
                            self.asset_graph.add_edge(chart, k)

        # add name if there's no title
        for k, v in self.asset_dict.items():
            if not v.name and "urn:li:dashboard:" in k:
                parsed = DashboardUrn.from_string(k)
                v.name = parsed.dashboard_id


class DatasetInfoParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.asset_dict.items():
            if "urn:li:dataset:" in k:
                urn = DatasetUrn.from_string(k)
                info_list = self.get_info(k)
                config = self.get_config(k)
                v.name = self.get_name(info_list)
                v.description = self.get_description(info_list)
                v.type = self.get_type(info_list)
                v.unique_name = self.get_unique_name(info_list) or urn.name
                if self.is_db:
                    v.db_location = urn.name.split(".")
                    v.materialization, incremental = self.get_materialization(info_list)
                    if incremental is not None:
                        config["incremental"] = incremental
                    v.sql = self.get_sql(info_list)

    def get_info(self, id):
        urn = DatasetUrn.from_string(id)
        if urn.platform == "urn:li:dataPlatform:dbt":
            dbt_info = self.row_dict.get(id, {}).get("datasetProperties", [])
            dbt_view_info = self.row_dict.get(id, {}).get("viewProperties", [])

            # these will not be found in the db by how asset_dict is constructed
            db_info = []
            db_view_info = []
        else:
            db_info = self.row_dict.get(id, {}).get("datasetProperties", [])
            db_view_info = self.row_dict.get(id, {}).get("viewProperties", [])

            # get dbt_id
            dbt_urn_str = DatasetUrn(
                platform="urn:li:dataPlatform:dbt", name=urn.name
            ).urn()
            dbt_info = self.row_dict.get(dbt_urn_str, {}).get("datasetProperties", [])
            dbt_view_info = self.row_dict.get(dbt_urn_str, {}).get("viewProperties", [])
        return dbt_info, db_info, dbt_view_info, db_view_info

    def get_name(self, info_list: list[dict[str, Any]]):
        dbt_info, db_info, _, _ = info_list
        for info in [*dbt_info, *db_info]:
            if "name" in info:
                return info["name"]
        return None

    def get_description(self, info_list: list[dict[str, Any]]):
        dbt_info, db_info, _, _ = info_list
        for info in [*dbt_info, *db_info]:
            if "description" in info:
                return info["description"]
        return None

    def get_type(self, info_list: list[dict[str, Any]]):
        dbt_info, db_info, _, _ = info_list
        for info in [*dbt_info, *db_info]:
            if "node_type" in info["customProperties"]:
                return info["customProperties"]["node_type"]
        return "dataset"

    def get_unique_name(self, info_list: list[dict[str, Any]]):
        dbt_info, _, _, _ = info_list
        for info in dbt_info:
            if "dbt_unique_id" in info["customProperties"]:
                return info["customProperties"]["dbt_unique_id"]

        return None

    def get_tags(self, info_list: list[dict[str, Any]]):
        dbt_info, db_info, _, _ = info_list
        tags = []
        for info in [*dbt_info, *db_info]:
            if "tags" in info:
                tags.extend(info["tags"])
        return list(set(tags))

    def get_materialization(self, info_list: list[dict[str, Any]]):
        dbt_info, db_info, _, db_view_info = info_list
        out_materialization = None
        out_incremental = None
        for info in dbt_info:
            if "materialization" in info["customProperties"]:
                materialization = info["customProperties"]["materialization"]
                if materialization == "view":
                    out_materialization = Asset.MaterializationType.VIEW
                    out_incremental = False
                elif materialization == "table" or materialization == "seed":
                    out_materialization = Asset.MaterializationType.TABLE
                    out_incremental = False
                elif materialization == "incremental":
                    out_materialization = Asset.MaterializationType.TABLE
                    out_incremental = True
                elif materialization == "materialized_view":
                    out_materialization = Asset.MaterializationType.MATERIALIZED_VIEW
                    out_incremental = False
                elif materialization == "ephemeral":
                    out_materialization = Asset.MaterializationType.EPHEMERAL
                    out_incremental = False

                return out_materialization, out_incremental

        is_view_db = False
        for info in db_info:
            if "is_view" in info["customProperties"]:
                is_view_db = info["customProperties"]["is_view"]

        is_materialized_db = False
        for info in db_view_info:
            if "materialized" in info:
                is_materialized_db = info["materialized"]

        if is_view_db and not is_materialized_db:
            out_materialization = Asset.MaterializationType.VIEW
        elif is_view_db and is_materialized_db:
            out_materialization = Asset.MaterializationType.MATERIALIZED_VIEW
        else:
            out_materialization = Asset.MaterializationType.TABLE

        return out_materialization, out_incremental

    def get_sql(self, info_list: list[dict[str, Any]]):
        dbt_info, _, dbt_view_info, db_view_info = info_list
        materialization = None
        for info in dbt_info:
            if "materialization" in info["customProperties"]:
                materialization = info["customProperties"]["materialization"]

        dbt_compiled_sql = None
        for info in dbt_view_info:
            if "formattedViewLogic" in info:
                dbt_compiled_sql = info["formattedViewLogic"]

        db_sql = None
        for info in db_view_info:
            if "viewLogic" in info:
                db_sql = info["viewLogic"]
                db_ast = sqlglot.parse(db_sql, dialect=self.dialect)[0]
                if isinstance(db_ast, exp.Create):
                    db_ast = db_ast.expression.copy()
                    db_sql = db_ast.sql(dialect=self.dialect)

        return dbt_compiled_sql or db_sql or None


class SchemaParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.asset_dict.items():
            if "urn:li:dataset:" in k:
                urn = DatasetUrn.from_string(k)
                info = self.get_info(k)
                self.get_fields(info, urn)

    def get_info(self, id):
        urn = DatasetUrn.from_string(id)
        if urn.platform == "urn:li:dataPlatform:dbt:":
            dbt_info = self.row_dict.get(id, {}).get("schemaMetadata", [])
        else:
            db_info = self.row_dict.get(id, {}).get("schemaMetadata", [])

            # get dbt_id
            db_urn = DatasetUrn.from_string(id)
            dbt_urn = DatasetUrn(platform="urn:li:dataPlatform:dbt", name=db_urn.name)
            dbt_id = dbt_urn.urn()
            dbt_info = self.row_dict.get(dbt_id, {}).get("schemaMetadata", [])
        return dbt_info, db_info

    def get_fields(self, info_list: list[dict[str, Any]], urn: DatasetUrn):
        dbt_info, db_info = info_list
        workspace_id = list(self.asset_dict.values())[
            0
        ].workspace_id  # all assets have the same tenant id
        for info in dbt_info:
            if "fields" in info:
                for field in info["fields"]:
                    ## ignore subfields
                    if "." in field["fieldPath"]:
                        continue
                    col_urn_str = SchemaFieldUrn(urn, field["fieldPath"]).urn()
                    self.column_dict[col_urn_str] = Column(
                        id=col_urn_str,
                        asset_id=urn.urn(),
                        name=field["fieldPath"],
                        type=field["nativeDataType"],
                        nullable=field["nullable"],
                        description=field.get("description"),
                        workspace_id=workspace_id,
                    )
        for info in db_info:
            if "fields" in info:
                for field in info["fields"]:
                    ## ignore subfields
                    if "." in field["fieldPath"]:
                        continue
                    col_urn_str = SchemaFieldUrn(urn, field["fieldPath"]).urn()
                    if col_urn_str in self.column_dict:
                        # only update type, which should default to postgres type
                        self.column_dict[col_urn_str].type = field["nativeDataType"]
                    else:
                        # build full Column based off of dbt info
                        self.column_dict[col_urn_str] = Column(
                            id=col_urn_str,
                            asset_id=urn.urn(),
                            name=field["fieldPath"],
                            type=field["nativeDataType"],
                            nullable=field["nullable"],
                            description=field.get("description"),
                            workspace_id=workspace_id,
                        )


class LineageParser(DataHubDBParserBase):
    def parse(self):
        for k, v in self.row_dict.items():
            if "upstreamLineage" in v:
                for lineage in v["upstreamLineage"]:
                    upstreams = lineage.get("upstreams", [])
                    if not isinstance(upstreams, list):
                        upstreams = [upstreams]

                    for upstream in upstreams:
                        self.asset_graph.add_edge(upstream["dataset"], k)

                    downstreams = lineage.get("downstreams", [])
                    if not isinstance(downstreams, list):
                        downstreams = [downstreams]
                    for downstream in downstreams:
                        self.asset_graph.add_edge(k, downstream)

                    if "fineGrainedLineages" in lineage and not self.is_db:
                        for field_info in lineage["fineGrainedLineages"]:
                            confidence_score = field_info["confidenceScore"]
                            for upstream_field in field_info["upstreams"]:
                                for downstream_field in field_info["downstreams"]:
                                    self.column_graph.add_edge(
                                        upstream_field,
                                        downstream_field,
                                        confidence_score=confidence_score,
                                    )


class AssertionParser(DataHubDBParserBase):
    # NOTE:dbt specific logic -- will need to be updated if we expand to other assertion types
    def parse(self):
        for k, v in self.row_dict.items():
            if "assertionInfo" in v:
                for info in v["assertionInfo"]:
                    self._parse_helper(info, k)

    def _parse_helper(self, info, assertion_urn):
        detail = info["customProperties"]["datasetAssertion"]
        test_name = detail["nativeType"]
        if dataset := detail.get("dataset") in self.asset_dict:
            adj_dataset = dataset
        else:
            # find db dataset equivalent
            dbt_urn = DatasetUrn.from_string(dataset)
            adj_dataset = None
            for urn_str in self.asset_dict:
                urn = DatasetUrn.from_string(urn_str)
                if urn.name == dbt_urn.name and urn.platform != dbt_urn.platform:
                    adj_dataset = urn_str
                    break

        if adj_dataset is None:
            raise ValueError(f"Could not link assertion {assertion_urn} to dataset")

        if detail.get("scope") == DatasetAssertionScope.DATASET_COLUMN:
            for field in detail["fields"]:
                adj_field_urn = SchemaFieldUrn(
                    adj_dataset,
                    SchemaFieldUrn.from_string(field).field_path,
                ).urn()
                if self.column_dict[adj_field_urn].tests is None:
                    self.column_dict[adj_field_urn].tests = []
                self.column_dict[adj_field_urn].tests.append(test_name)
        else:
            # this means it's represented as a dbt asset
            if self.asset_dict[adj_dataset].tests is None:
                self.asset_dict[adj_dataset].tests = []
            self.asset_dict[adj_dataset].tests.append(test_name)


class DataHubDBParser:
    query: str = "select * from metadata_aspect_v2 where version = 1"
    input_dict: dict[str, Any]
    asset_dict: dict[str, Asset]
    column_dict: dict[str, Column]
    asset_graph: nx.DiGraph
    column_graph: nx.MultiDiGraph
    asset_links: list[AssetLink]
    asset_errors: list[AssetError]
    column_links: list[ColumnLink]

    def __init__(
        self,
        resource: Resource,
        path: str | None = os.path.expanduser("~/.datahub/lite/datahub.duckdb"),
    ):
        self.path = path
        self.resource_id = resource.id
        self.workspace_id = resource.workspace.id
        self.dialect = resource.details.subtype
        self.is_db = resource.type == ResourceType.DB

        # initialize outputs
        self.input_dict = {}
        self.asset_dict = {}
        self.column_dict = {}
        self.asset_graph = nx.DiGraph()
        self.column_graph = nx.MultiDiGraph()
        self.asset_links = []
        self.asset_errors = []
        self.column_links = []

    def get_data(self):
        if self.path is None:
            raise ValueError("Path not set")

        return duckdb.connect(self.path, read_only=True).execute(self.query).fetchall()

    def get_row_dict(self):
        base_asset_dict = {}
        for row in self.get_data():
            id = row[0]
            if self.exclude_node(id):
                continue
            self.input_dict.setdefault(id, {}).setdefault(row[1], []).append(
                orjson.loads(row[3])
            )
            base_asset_dict.setdefault(
                id,
                Asset(
                    id=id, resource_id=self.resource_id, workspace_id=self.workspace_id
                ),
            )
        if self.is_db:
            # remove from asset_dict dbt assets that are materialized in a db. We'll use the postgres id as the source_of_truth
            self.duplicate_helper = get_duplicate_nodes_helper(
                base_asset_dict.keys(), base_prioritization_f
            )

            # just keep first value. This is how duplicate helper works
            for val in self.duplicate_helper.values():
                self.asset_dict[val[0]] = base_asset_dict[val[0]]
        else:
            self.asset_dict = base_asset_dict

    @classmethod
    def exclude_node(cls, id: str):
        if "urn:li:container" in id or "urn:li:tag" in id or "urn:li:assertion" in id:
            return True
        return False

    def graph_contraction_helper(self, type: Literal["asset", "column"]):
        """
        Helper function to contract the graph. Unifies dbt and non-dbt nodes otherwise removes and reconnects nodes.
        """
        if type == "asset":
            graph = self.asset_graph
            helper_dict = get_duplicate_nodes_helper(
                self.asset_graph.nodes, lambda x: x in self.asset_dict
            )
        else:
            # NOTE: need to adjust to make work correctly for columns, but not used now because column lineage is parsed manually
            graph = self.column_graph
            helper_dict = get_duplicate_nodes_helper(
                self.column_graph.nodes, lambda x: x in self.column_dict
            )
        if len(graph.nodes) == 0:
            return

        helper_dict = {v[0]: v for v in helper_dict.values()}
        for node in nx.topological_sort(graph.copy()):
            vals = helper_dict.get(node)
            if vals is None:
                continue
            u, *vs = vals
            for v in vs:
                if v not in graph:
                    continue

                nx.contracted_nodes(
                    graph,
                    u,
                    v,
                    self_loops=False,
                    copy=False,
                )

    def adjust_asset_graphs_and_dicts(self):
        for id in self.asset_dict:
            if id not in self.asset_graph:
                self.asset_graph.add_node(id)

        if self.is_db:
            self.graph_contraction_helper("asset")

    def _get_dbt_field_urn(self, id: str):
        parsed = SchemaFieldUrn.from_string(id)
        db_urn = DatasetUrn.from_string(parsed.parent)
        dbt_field_urn = SchemaFieldUrn(
            DatasetUrn(platform="urn:li:dataPlatform:dbt", name=db_urn.name),
            parsed.field_path,
        ).urn()
        return dbt_field_urn

    def adjust_column_graphs_and_dicts(self):
        if self.is_db:
            self.graph_contraction_helper("column")

        # else:
        #     for node in self.column_graph.nodes:
        #         if node not in self.column_dict:
        #             underlying_asset_id = SchemaFieldUrn.from_string(node).parent
        #             self.column_dict[node] = Column(
        #                 id=node,
        #                 asset_id=underlying_asset_id,
        #                 workspace_id=self.workspace_id,
        #             )

        # make sure unconnected nodes are in the graph
        for id in self.column_dict:
            if id not in self.column_graph:
                self.column_graph.add_node(id)

    def get_links(self):
        for u, v in self.asset_graph.edges:
            self.asset_links.append(
                AssetLink(
                    id=f"{u}_{v}",
                    workspace_id=self.workspace_id,
                    source_id=u,
                    target_id=v,
                )
            )
        for u, v, data in self.column_graph.edges(data=True):
            if connection_types := data.get("ntype"):
                connection_types = list(connection_types)
            else:
                connection_types = None

            lineage_type = data.get("lineage_type")

            self.column_links.append(
                ColumnLink(
                    id=f"{u}_{v}_{lineage_type}",
                    workspace_id=self.workspace_id,
                    source_id=u,
                    target_id=v,
                    lineage_type=lineage_type,
                    connection_types=connection_types,
                )
            )

    def get_outputs(self):
        return {
            "assets": list(self.asset_dict.values()),
            "columns": list(self.column_dict.values()),
            "asset_links": self.asset_links,
            "column_links": self.column_links,
            "asset_errors": self.asset_errors,
        }

    def get_sqlglot_table_helper(self, k: str):
        catalog, schema, *table_list = DatasetUrn.from_string(k).name.split(".")
        table = ".".join(table_list)
        return exp.Table(
            catalog=exp.Identifier(this=catalog),
            db=exp.Identifier(this=schema),
            this=exp.Identifier(this=table),
        )

    def get_asset_column_dict(self):
        self.asset_column_dict = {}
        for col in self.column_dict.values():
            if "." in col.name:
                print(col.asset.id, col.name)
            self.asset_column_dict.setdefault(col.asset_id, []).append(col.name)

    def get_schema_helper(self, k: str):
        # asset_column_dict already created in prior step of cll workflow
        schema_helper = [
            (col_name, str) for col_name in self.asset_column_dict.get(k, [])
        ]
        # schema_tples = []
        # for col in self.column_dict.values():
        #     if col.asset_id == k:
        #         schema_tples.append((col.name, str))
        return VinylSchema(ibis.schema(schema_helper))

    # @timeout(15)
    def get_ast_nodes(
        self, k: str, asset: Asset, lineage_types: list[ColumnLink.LineageType]
    ) -> SQLAstNode:
        node = SQLAstNode(
            id=k,
            dialect=self.dialect,
            use_datahub_nodes=True,
            errors=[],
        )
        catalog = DatasetUrn.from_string(k).name.split(".")[0]
        try:
            node.ast = sqlglot.parse(asset.sql, dialect=self.dialect)[0]
            node.original_ast = node.ast.copy()
        except ParseError as e:
            node.errors.append(
                VinylError(
                    node_id=k,
                    type=VinylErrorType.PARSE_ERROR,
                    msg=str(e),
                    traceback=traceback.format_exc(),
                    dialect=self.dialect,
                )
            )

        # ensure all table references have a catalog. Some dialects omit this
        def ensure_table_catalog(node: Expression) -> Expression:
            if (
                isinstance(node, exp.Table)
                and node.db is not None
                and node.catalog is None
            ):
                return exp.Table(catalog=catalog, db=node.db, this=node.this)
            return node

        node.ast.transform(ensure_table_catalog)

        # add in schema info. But fake type info in because it's not necessary for lineage
        node.schema = {self.get_sqlglot_table_helper(k): self.get_schema_helper(k)}

        if k in self.asset_graph.nodes:
            node.deps = []
            node.deps_schemas = {}
            for dep in self.asset_graph.predecessors(k):
                if dep in self.asset_dict:
                    node.deps.append(dep)
                    node.deps_schemas[self.get_sqlglot_table_helper(dep)] = (
                        self.get_schema_helper(dep)
                    )
        node.optimize()

        nodes = []
        for ltype in lineage_types:
            node_it = copy.deepcopy(node)
            node_it.get_lineage(lineage_filters=ltype.connection_types())
            nodes.append(node_it)

        return nodes

    # @pyprofile(save_html=True)
    def get_db_cll(self):
        self.get_asset_column_dict()
        asset_dict_items = self.asset_dict.items()
        # if os.getenv("DEV") == "true":
        #     asset_dict_items = tqdm(
        #         asset_dict_items,
        #         desc="Getting lineage...",
        #     )
        graphs = []
        for j, (k, asset) in enumerate(asset_dict_items):
            if not asset.sql:
                continue

            if os.getenv("DEV") == "true":
                print(j, k)

            ltypes = [ltype for ltype in ColumnLink.LineageType]

            nodes = self.get_ast_nodes(k, asset, ltypes)
            for i, node in enumerate(nodes):
                if node.errors:
                    for error in node.errors:
                        error = AssetError(asset=asset, error=error.to_dict())
                        if error not in self.asset_errors:
                            print("error", error)
                            print(error.error)
                            self.asset_errors.append(error)
                lineage = node.lineage.to_networkx()
                nx.set_edge_attributes(
                    lineage,
                    {e: {"lineage_type": ltypes[i].value} for e in lineage.edges},
                )
                lineage = nx.MultiDiGraph(lineage)
                graphs.append(lineage)

                # make sure no silent lineage failures
                if (
                    len(lineage.edges) == 0
                    and len(node.deps) > 0
                    and len(node.errors) == 0
                ):
                    vinylerror = VinylError(
                        node_id=k,
                        type=VinylErrorType.NO_LINEAGE_ERROR,
                        msg="No lineage found for asset despite node having dependencies and lack of explicit lineage errors",
                        dialect=self.dialect,
                        context=node.original_ast.sql(dialect=self.dialect),
                    )
                    error = AssetError(asset=asset, error=vinylerror.to_dict())
                    if error not in self.asset_errors:
                        self.asset_errors.append(error)
                        print("uncaught error", error)
        self.column_graph = nx.compose_all([self.column_graph, *graphs])

        # remove malformed nodes from the graph
        for node in self.column_graph.copy():
            try:
                SchemaFieldUrn.from_string(node)
            except (InvalidUrnError, AssertionError):
                nx_remove_node_and_reconnect(
                    self.column_graph, node, preserve_ntype=True
                )

    def parse(self):
        self.get_row_dict()
        for i, cls in enumerate(DataHubDBParserBase.__subclasses__()):
            if i == 0:
                parser = cls(
                    row_dict=self.input_dict,
                    asset_dict=self.asset_dict,
                    dialect=self.dialect,
                    is_db=self.is_db,
                )
            else:
                parser = cls(**parser.get_outputs())
            parser.parse()

        outputs = parser.get_outputs()
        self.asset_dict = outputs["asset_dict"]
        self.column_dict = outputs["column_dict"]
        self.asset_graph = outputs["asset_graph"]
        self.column_graph = outputs["column_graph"]

        self.adjust_asset_graphs_and_dicts()
        self.adjust_column_graphs_and_dicts()
        if self.is_db:
            self.get_db_cll()

    @classmethod
    def combine(cls, parsers: list[DataHubDBParser], resource: Resource):
        combined = DataHubDBParser(resource=resource)  # dummy resource
        for i, parser in enumerate(parsers):
            combined.asset_dict.update(parser.asset_dict)
            combined.column_dict.update(parser.column_dict)
            combined.asset_graph = nx.compose(combined.asset_graph, parser.asset_graph)
            combined.column_graph = nx.compose(
                combined.column_graph, parser.column_graph
            )
            combined.asset_errors.extend(parser.asset_errors)

        # get links after combining to ensure parent asset from another resource is avaiable when you do
        combined.get_links()

        return combined.get_outputs()

    @classmethod
    def _get_indirect_asset(
        cls, id: str, all_resource_dict: dict[str, Resource], resource: Resource
    ):
        if "urn:li:dataset:" in id:
            urn = DatasetUrn.from_string(id)
            resource_name = urn.platform.split(":")[-1]
            asset_name = urn.name
            asset_type = Asset.AssetType.DATASET

        elif "urn:li:chart:" in id:
            urn = ChartUrn.from_string(id)
            resource_name = urn.dashboard_tool
            asset_name = urn.chart_id
            asset_type = Asset.AssetType.CHART

        elif "urn:li:dashboard:" in id:
            urn = DashboardUrn.from_string(id)
            resource_name = urn.dashboard_tool
            asset_name = urn.dashboard_id
            asset_type = Asset.AssetType.DASHBOARD

        else:
            raise ValueError(f"Unrecognized asset type for {id}")

        ### if explicit resource doesn't exist (e.g. is dbt), use the resource that was passed in
        resource_it = all_resource_dict.get(resource_name, resource)
        return Asset(id=id, name=asset_name, type=asset_type, resource=resource_it)

    @classmethod
    def combine_and_upload(cls, parsers: list[DataHubDBParser], resource: Resource):
        combined = cls.combine(parsers, resource)
        all_resource_dict = {
            resource.details.subtype: resource
            for resource in resource.workspace.resource_set.all()
        }
        indirect_assets = []
        indirect_columns = []

        ## ensure all assets in the graph exist in the db so you don't key a fk error
        asset_ids_to_add = set(
            [v.source_id for v in combined["asset_links"]]
            + [v.target_id for v in combined["asset_links"]]
        ) - set([v.id for v in combined["assets"]])

        for id in asset_ids_to_add:
            asset = cls._get_indirect_asset(id, all_resource_dict, resource)
            indirect_assets.append(asset)

        ## ensure all columns in the graph exist in the db so you don't key a fk error
        columns_to_add = set(
            [v.source_id for v in combined["column_links"]]
            + [v.target_id for v in combined["column_links"]]
        ) - set([v.id for v in combined["columns"]])
        for column_id in columns_to_add:
            parsed = SchemaFieldUrn.from_string(column_id)
            asset_id = parsed.parent
            if asset_id not in combined["assets"] and asset_id not in indirect_assets:
                asset = cls._get_indirect_asset(asset_id, all_resource_dict, resource)
                indirect_assets.append(asset)
            column = Column(
                id=column_id,
                asset_id=asset_id,
                name=parsed.field_path,
                nullable=True,
            )
            indirect_columns.append(column)

        breakpoint()

        delete_and_upsert(combined["assets"], resource, indirect_assets)
        delete_and_upsert(combined["asset_errors"], resource)
        delete_and_upsert(combined["asset_links"], resource)
        delete_and_upsert(combined["columns"], resource, indirect_columns)
        delete_and_upsert(combined["column_links"], resource)
