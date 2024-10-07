import networkx as nx

from app.models import Asset, Column
from vinyl.lib.dbt import DBTProject


def get_manifest_node(proj: DBTProject, node_id: str, defer: bool = False):
    proj.mount_manifest(defer=defer)
    if node_id in proj.manifest["nodes"]:
        manifest_node = proj.manifest["nodes"][node_id]
    elif node_id in proj.manifest["sources"]:
        manifest_node = proj.manifest["sources"][node_id]
    else:
        manifest_node = None
    return manifest_node


def get_catalog_node(proj: DBTProject, node_id: str, defer: bool = False):
    proj.mount_catalog(defer=defer)
    if node_id in proj.catalog["nodes"]:
        catalog_node = proj.catalog["nodes"][node_id]
    elif node_id in proj.catalog["sources"]:
        catalog_node = proj.catalog["sources"][node_id]
    else:
        catalog_node = None
    return catalog_node


def get_lineage(
    proj: DBTProject,
    node_ids: list[str],
    resource_id: str,
    workspace_id: str,
    predecessor_depth: int | None = 1,
    successor_depth: int | None = 1,
    defer: bool = False,
):
    proj.mount_manifest(defer=defer)
    proj.build_model_graph()
    all_downstream_nodes = proj.model_graph.get_relatives(
        node_ids, depth=successor_depth
    )
    all_upstream_nodes = proj.model_graph.get_relatives(
        node_ids, reverse=True, depth=predecessor_depth
    )
    if predecessor_depth is not None:
        lineage_upstream_nodes = proj.model_graph.get_relatives(
            node_ids, reverse=True, depth=predecessor_depth - 1
        )
    else:
        lineage_upstream_nodes = []
    all_nodes = list(set(all_upstream_nodes + all_downstream_nodes))
    lineage_nodes = list(set(lineage_upstream_nodes + all_downstream_nodes))
    asset_graph = proj.model_graph.subgraph(all_nodes).to_networkx()
    asset_dict = {}
    asset_errors = []
    column_dict = {}
    id_map = {}
    for node_id in all_nodes:
        manifest_node = get_manifest_node(proj, node_id, defer=defer)
        db_location = proj.get_relation_name(node_id).replace('"', "").replace("`", "")
        asset_id = f"urn:li:dataset:(urn:li:dataPlatform:dbt,{db_location},PROD)"
        id_map[node_id] = asset_id
        asset = Asset(
            id=asset_id,
            name=manifest_node["name"],
            type=manifest_node["resource_type"],
            unique_name=node_id,
            db_location=db_location.split("."),
            resource_id=resource_id,
            workspace_id=workspace_id,
        )
        compiled_sql, error = proj.get_compiled_sql(node_id, defer=defer, errors=[])
        if error:
            asset_errors.append(error)
        else:
            asset.sql = compiled_sql
        catalog_node = get_catalog_node(proj, node_id, defer=defer)
        if catalog_node is not None:
            for k, v in catalog_node["columns"].items():
                column_id = f"urn:li:SchemaField:({asset_id},{k})"
                column = Column(id=column_id, name=k, asset_id=asset_id, type=v["type"])
                column_dict[column_id] = column
        asset_dict[asset_id] = asset
    nx.relabel_nodes(asset_graph, id_map)
    breakpoint()

    # sqlastnodes = []
    # sorted = [
    #     n for n in self.model_graph.topological_sort() if n in nodes_to_consider
    # ]
    # for node in sorted:
    #     sqlastnode = SQLAstNode(id=node)
    #     compiled_sql, error = self.get_compiled_sql(node, defer=defer, errors=[])
    #     if error:
    #         sqlastnode.errors = [error]
    #         continue

    #     try:
    #         sqlastnode.ast = sqlglot.parse_one(
    #             compiled_sql, dialect=self.dialect.value
    #             )
    #         sqlastnode.original_ast = sqlastnode.ast.copy()
    #     except ParseError as e:
    #         sqlastnode.errors.append(
    #             VinylError(
    #                 node_id=node,
    #                 type=VinylErrorType.PARSE_ERROR,
    #                 msg=str(e),
    #                 traceback=traceback.format_exc(),
    #                 dialect=self.dialect,
    #             )
    #         sqlastnode.deps = self.model_graph.get_parents([node])
    #         sqlastnode.deps_schemas = self.get_lineage_schema(sqlastnode.deps)
    #         sqlastnode.get_lineage()
    #     sqlastnodes.append(sqlastnode)

    breakpoint()


#  def get_lineage_schema(self, node_ids: list[str], defer: bool = False):
#         self.mount_catalog(defer=defer)
#         schema = {}
#         for node in node_ids:
#             if node in self.catalog["nodes"]:
#                 catalog_node = self.catalog["nodes"][node]
#             elif node in self.catalog["sources"]:
#                 catalog_node = self.catalog["sources"][node]
#             else:
#                 catalog_node = None
#             if catalog_node is not None:
#                 schema[node] = {}
#             else:
#                 schema[node] = {
#                     k: v["type"] for k, v in catalog_node["columns"].items()
#                 }
#         return schema
