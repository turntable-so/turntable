from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Any, Literal, TypeAlias

import ibis
import ibis.expr.types as ir
import rustworkx as rx

from vinyl.lib.field import Field
from vinyl.lib.graph import VinylGraph
from vinyl.lib.utils.sequence import _find_min_length_list_index

base_join_type: TypeAlias = (
    str
    | ir.BooleanColumn
    | Literal[True]
    | Literal[False]
    | tuple[
        str | ir.Column,
        str | ir.Column,
    ]
)

AUTO_JOIN_DEFAULT_HOW = "left"
MANUAL_JOIN_DEFAULT_HOW = "inner"


class JoinNodeInfo:
    _u_op: ir.Expr | None
    _u_col_name: str
    _v_name: str
    _source_tbl: ir.Expr
    _source_vinyl_table: Any  # will be VinylTable

    def _get_field(self):
        return getattr(self._source_vinyl_table._source_class, self._u_col_name)


class JoinHelper:
    _hash_: str
    _join_index: int
    _node_dict: dict[ir.Expr, ir.Expr]
    _node_info: list[JoinNodeInfo]


@lru_cache(None)
def _get_path(g: rx.PyDiGraph, u: int, v: int) -> rx.PathMapping:
    return rx.dijkstra_shortest_paths(g, source=u, target=v)  # type: ignore[attr-defined]


def _get_routes(
    g: rx.PyDiGraph, tbl_locations: list[int], len_=None
) -> list[list[int] | None]:
    if len is None:
        path_options = [list(p) for p in itertools.permutations(tbl_locations)]
    else:
        path_options = [list(p) for p in itertools.permutations(tbl_locations, len_)]

    # caching inside function so we don't recalucate where we don't need to
    path_routes = []
    for path in path_options:
        path_route_it: list[int] | None = []
        for i, loc in enumerate(path):
            if path_route_it is None:
                continue
            if i < len(path) - 1:
                subpath = _get_path(g, loc, path[i + 1])
                if not subpath:
                    path_route_it = None
                    continue

                subpath_keys = [j for j in [i for i in subpath.values()][0]]
                if len(path_route_it) != 0:
                    path_route_it.pop(-1)
                path_route_it.extend(subpath_keys)
        path_routes.append(path_route_it)

    return path_routes


def _get_path_nodes_and_edges(
    non_trivial_g: rx.PyDiGraph, path_routes: list[list[int] | None]
) -> tuple[list[int], list[Any], list[tuple[str, str] | bool]]:
    # find the shortest path
    min_path_index = _find_min_length_list_index(path_routes)
    if min_path_index is None:
        raise ValueError("No join path found, please join manually")
    final_route = path_routes[min_path_index]
    if final_route is None:
        raise ValueError("No join path found, please join manually")
    final_node_values = [non_trivial_g[i] for i in final_route]
    edge_index_pairs = [i for i in non_trivial_g.edge_list()]
    edge_values = non_trivial_g.edges()
    path_edges = []
    for i, key in enumerate(final_route):
        if i < len(final_route) - 1:
            index = edge_index_pairs.index((key, final_route[i + 1]))
            path_edges.append(edge_values[index])

    return final_route, final_node_values, path_edges


def _auto_join_helper(
    tbls: list[ir.Expr], allow_cross_join: bool = False
) -> tuple[list[ir.Expr], list[tuple[str, str] | bool]]:
    g = Field._relations
    non_trivial_connections: set[int] = set()
    for se in rx.weakly_connected_components(g):  # type: ignore[attr-defined]
        if len(se) > 1:
            non_trivial_connections = non_trivial_connections.union(se)
    non_trivial_g = g.subgraph(list(non_trivial_connections))
    node_hash = {}
    node_dict_store = {}

    # prepare data
    tbl_dict: dict[str, JoinHelper] = {}
    for tbl in tbls:
        hash_ = str(hash(tbl))
        tbl_dict[hash_] = base_it = JoinHelper()
        if hash_ not in node_hash:
            base_it._join_index = node_hash[hash_] = non_trivial_g.add_node(tbl)
        else:
            base_it._join_index = node_hash[hash_]
        node_dict_store[base_it._join_index] = base_it._node_dict = (
            VinylGraph._find_unaltered_cols(tbl)
        )
        base_it._node_info = []
        for u, v in base_it._node_dict.items():
            node_info = JoinNodeInfo()
            node_info._u_op = u.op()
            node_info._u_col_name = u.get_name()
            node_info._source_tbl = node_info._u_op.args[0].to_expr()
            node_info._source_vinyl_table = Field._source_adj_tbl_dict[
                str(hash(node_info._source_tbl))
            ]
            node_info._v_name = v.name
            base_it._node_info.append(node_info)

    non_trivial_nodes = non_trivial_g.nodes()

    # make n = 1 leaps
    for tbl, base_it in tbl_dict.items():
        for base_info in base_it._node_info:
            for i, node in enumerate(non_trivial_nodes):
                # find which source node is relevant
                if hash(node) == hash(base_info._source_vinyl_table):
                    # check which column type it is
                    field = base_info._get_field()
                    if field.primary_key or field.unique:
                        # connect to the source node in both directions
                        non_trivial_g.add_edge(
                            i,
                            base_it._join_index,
                            (base_info._u_col_name, base_info._v_name),
                        )
                        non_trivial_g.add_edge(
                            base_it._join_index,
                            i,
                            (base_info._v_name, base_info._u_col_name),
                        )

    # make n = 2 and n = 3 leaps
    for tbl, base_it in tbl_dict.items():
        for base_info in base_it._node_info:
            for i, node in enumerate(non_trivial_nodes):
                # find which source node is relevant
                if hash(node) == hash(base_info._source_vinyl_table):
                    # make foreign degree connections
                    field = base_info._get_field()
                    if field.foreign_key is not None:
                        in_edges = non_trivial_g.in_edges(i)
                        for edge in in_edges:
                            in_col, out_col = edge[-1]
                            if out_col == base_info._u_col_name:
                                # make second degree connections
                                non_trivial_g.add_edge(
                                    edge[0],
                                    base_it._join_index,
                                    (in_col, base_info._v_name),
                                )
                                edges2 = non_trivial_g.in_edges(edge[0])
                                for edge2 in edges2:
                                    in_col2, out_col2 = edge2[-1]
                                    if out_col2 == in_col:
                                        # make third degree connections
                                        non_trivial_g.add_edge(
                                            edge2[0],
                                            base_it._join_index,
                                            (in_col2, base_info._v_name),
                                        )
                    # make primary key connections
                    if field.primary_key:
                        out_edges = non_trivial_g.out_edges(i)
                        for edge in out_edges:
                            in_col, out_col = edge[-1]
                            if in_col == base_info._u_col_name:
                                # make second degree connections
                                non_trivial_g.add_edge(
                                    base_it._join_index,
                                    edge[1],
                                    (base_info._v_name, out_col),
                                )
                                edges2 = non_trivial_g.out_edges(edge[1])
                                for edge2 in edges2:
                                    in_col2, out_col2 = edge2[-1]
                                    if in_col2 == out_col:
                                        # make third degree connections
                                        non_trivial_g.add_edge(
                                            base_it._join_index,
                                            edge2[1],
                                            (base_info._v_name, out_col2),
                                        )
    # find shortest path
    tbl_locations = [i for i in node_dict_store.keys()]
    path_routes = _get_routes(non_trivial_g, tbl_locations)

    # find the shortest path
    try:
        final_route, final_node_values, path_edges = _get_path_nodes_and_edges(
            non_trivial_g, path_routes
        )
        return final_node_values, path_edges

    except ValueError:
        span = len(tbls)
        if not allow_cross_join:
            raise ValueError(
                "No join path found and cross joins not allowed, please join manually"
            )
        elif span == 2:
            return tbls, [True]  # cross join
        else:
            path_routes_wo1 = _get_routes(non_trivial_g, tbl_locations, len_=span - 1)
            try:
                # up to one cross join is allowed, otherwise error out
                (
                    final_route_wo1,
                    final_node_values_wo1,
                    path_edge_wo1,
                ) = _get_path_nodes_and_edges(non_trivial_g, path_routes_wo1)
                excluded_tbl_num = list(set(tbl_locations) - set(final_route))
                assert len(excluded_tbl_num) == 1
                excluded_tbl = non_trivial_g[excluded_tbl_num[0]]
                return final_node_values_wo1 + [excluded_tbl], path_edge_wo1 + [True]

            except ValueError:
                raise ValueError(
                    "No join path found for more than  tables, please join manually"
                )


def _convert_auto_join_to_ibis_join(
    final_nodes: list[Any],
    edges: list[tuple[str, str] | bool],
    how: Literal[
        "inner",
        "left",
        "outer",
        "right",
        "semi",
        "anti",
        "any_inner",
        "any_left",
        "left_semi",
    ] = AUTO_JOIN_DEFAULT_HOW,  # type: ignore[assignment]
) -> Any:
    # convert to ibis join
    for (
        i,
        node,
    ) in enumerate(final_nodes):
        if i == len(final_nodes) - 1:
            break

        edge: tuple[str, str] | bool = edges[i]

        if isinstance(edge, bool):
            predicate: list[tuple[str, str] | bool] = [edge]
        else:
            predicate = [(edge[0], edge[1])]

        if i == 0:
            join = ibis.join(
                left=node.tbl,
                right=final_nodes[i + 1].tbl,
                how=how,
                predicates=predicate,
            )
        else:
            join = ibis.join(
                left=join.tbl,
                right=final_nodes[i + 1].tbl,
                how=how,
                predicates=predicate,
            )
    return join
