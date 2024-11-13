import networkx as nx

from app.core.e2e import DataHubDBParser
from app.models import Asset, AssetError, Column, ColumnLink, Resource
from app.services.lineage_service import Lineage
from vinyl.lib.dbt import DBTProject, DBTTransition


class LiveDBTParser:
    resource: Resource
    asset_id: str
    asset_graph: nx.MultiDiGraph
    asset_dict: dict[str, Asset]
    asset_errors: list[AssetError]
    column_dict: dict[str, Column]
    all_nodes: list[str]  # assets included in final output
    lineage_nodes: list[str]  # assets on which lineage is explicitly calculated
    catalog_nodes: list[str]  # assets whose catalog info is necessary to parse lineage
    id_map: dict[str, str]

    def __init__(
        self,
        resource: Resource,
    ):
        self.resource = resource

        self.asset_dict = {}
        self.asset_errors = []
        self.column_dict = {}

    @classmethod
    def get_manifest_node(cls, proj: DBTProject, node_id: str, defer: bool = False):
        proj.mount_manifest(defer=defer)
        if node_id in proj.manifest["nodes"]:
            manifest_node = proj.manifest["nodes"][node_id]
        elif node_id in proj.manifest["sources"]:
            manifest_node = proj.manifest["sources"][node_id]
        else:
            manifest_node = None
        return manifest_node

    @classmethod
    def get_catalog_node(cls, proj: DBTProject, node_id: str, defer: bool = False):
        proj.mount_catalog(defer=defer)
        if node_id in proj.catalog["nodes"]:
            catalog_node = proj.catalog["nodes"][node_id]
        elif node_id in proj.catalog["sources"]:
            catalog_node = proj.catalog["sources"][node_id]
        else:
            catalog_node = None
        return catalog_node

    @classmethod
    def get_node_id_from_filepath(
        cls, proj: DBTProject, filepath: str, defer: bool = False
    ):
        proj.mount_manifest(defer=defer)
        for node_id, node in proj.manifest["nodes"].items():
            if node["original_file_path"] == filepath:
                return node_id
        return None

    @classmethod
    def parse_project(
        cls,
        proj: DBTProject,
        node_id: str,
        resource: Resource,
        before_proj: DBTProject | None = None,
        predecessor_depth: int | None = 1,
        successor_depth: int | None = 1,
        defer: bool = False,
        asset_only: bool = False,
    ):
        if before_proj is not None:
            transition = DBTTransition(before_proj, proj)
            transition.mount_manifest(defer=defer)
            transition.mount_catalog(defer=defer)
        else:
            proj.mount_manifest(defer=defer)
            proj.mount_catalog(defer=defer)

        proj.build_model_graph()
        all_downstream_nodes = proj.model_graph.get_relatives(
            [node_id], depth=successor_depth
        )
        all_upstream_nodes = proj.model_graph.get_relatives(
            [node_id], reverse=True, depth=predecessor_depth
        )
        if predecessor_depth is not None:
            lineage_upstream_nodes = proj.model_graph.get_relatives(
                [node_id], reverse=True, depth=max(predecessor_depth - 1, 0)
            )
        else:
            lineage_upstream_nodes = []
        out = cls(resource=resource)
        out.all_nodes = list(set(all_upstream_nodes + all_downstream_nodes))
        out.lineage_nodes = list(set(lineage_upstream_nodes + all_downstream_nodes))
        lineage_parents = proj.model_graph.get_relatives(
            out.lineage_nodes, depth=1, reverse=True
        )
        out.catalog_nodes = list(set(out.lineage_nodes + lineage_parents))
        out.asset_graph = proj.model_graph.subgraph(out.catalog_nodes).to_networkx()
        out.id_map = {}

        # compile sql for relevant nodes
        if not asset_only:
            if before_proj is not None:
                before_proj.dbt_compile(
                    [n for n in out.lineage_nodes if n in before_proj.manifest["nodes"]]
                )
            proj.dbt_compile(out.lineage_nodes, defer=defer)

        # process nodes
        for nid in out.catalog_nodes:
            manifest_node = out.get_manifest_node(proj, nid, defer=defer)
            db_location = proj.get_relation_name(nid).replace('"', "").replace("`", "")
            if not db_location:
                continue
            asset_id = f"urn:li:dataset:(urn:li:dataPlatform:{proj.dialect.value},{db_location},PROD)"
            out.id_map[nid] = asset_id
            asset = Asset(
                id=asset_id,
                name=manifest_node.get("name"),
                description=manifest_node.get("description"),
                materialization=manifest_node.get("config", {}).get("materialized"),
                tags=manifest_node.get("tags"),
                type=manifest_node.get("resource_type"),
                unique_name=nid,
                db_location=db_location.split("."),
                resource_id=resource.id,
                workspace_id=resource.workspace.id,
            )
            if not asset_only:
                compiled_sql, error = proj.get_compiled_sql(nid, defer=defer, errors=[])

                if error:
                    out.asset_errors.append(error)
                else:
                    asset.sql = compiled_sql
            out.asset_dict[asset_id] = asset

            # build column info
            if not asset_only:
                catalog_node = out.get_catalog_node(proj, nid, defer=defer)
                if catalog_node is not None:
                    for k, v in catalog_node["columns"].items():
                        column_id = f"urn:li:schemaField:({asset_id},{k})"
                        column = Column(
                            id=column_id,
                            name=k,
                            asset_id=asset_id,
                            type=v["type"],
                            workspace_id=resource.workspace.id,
                            description=manifest_node.get("columns", {})
                            .get(k, {})
                            .get("description"),
                        )
                        out.column_dict[column_id] = column
        nx.relabel_nodes(out.asset_graph, out.id_map, copy=False)
        out.asset_id = out.id_map[node_id]
        return out

    def filter_out_catalog_nodes_and_column_links(
        self, obj: Lineage, lineage_type: ColumnLink.LineageType
    ):
        all_node_ids = [v for k, v in self.id_map.items() if k in self.all_nodes]
        obj.assets = [asset for asset in obj.assets if asset.id in all_node_ids]
        obj.asset_links = [
            link
            for link in obj.asset_links
            if link.source_id in all_node_ids and link.target_id in all_node_ids
        ]
        obj.columns = [
            column for column in obj.columns if column.asset_id in all_node_ids
        ]
        column_ids = [column.id for column in obj.columns]
        obj.column_links = [
            link
            for link in obj.column_links
            if link.source_id in column_ids
            and link.target_id in column_ids
            and link.lineage_type == lineage_type
        ]
        return obj

    def get_lineage(
        self,
        lineage_type: ColumnLink.LineageType = ColumnLink.LineageType.ALL,
        asset_only: bool = False,
    ) -> tuple[Lineage, list[AssetError]]:
        parser = DataHubDBParser(resource=self.resource)
        parser.asset_dict = self.asset_dict
        parser.asset_graph = self.asset_graph
        parser.asset_errors = self.asset_errors
        ignore_dbt_ids = set(self.catalog_nodes) - set(self.lineage_nodes)
        ignore_ids = [self.id_map[k] for k in ignore_dbt_ids]

        if not asset_only:
            parser.column_dict = self.column_dict
            parser.get_db_cll(ignore_ids=ignore_ids)
        parser.get_links()

        raw_lineage = Lineage(
            asset_id=self.asset_id,
            assets=list(parser.asset_dict.values()),
            asset_links=parser.asset_links,
            columns=list(parser.column_dict.values()),
            column_links=parser.column_links,
        )
        return (
            self.filter_out_catalog_nodes_and_column_links(raw_lineage, lineage_type),
            parser.asset_errors,
        )
