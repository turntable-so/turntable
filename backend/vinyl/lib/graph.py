from __future__ import annotations

from collections import Counter

import ibis
import ibis.expr.operations as ops
import ibis.expr.types as ir
import ibis.selectors as s
import networkx as nx
import rustworkx as rx
from ibis.backends import BaseBackend
from ibis.common.collections import FrozenDict
from rich.console import Console
from rich.text import Text  # noqa: F401
from textual.app import ComposeResult
from textual.widgets import Footer
from vinyl.lib.utils.context import _is_notebook
from vinyl.lib.utils.graph import _get_label, _rustworkx_to_networkx
from vinyl.lib.utils.graphics import TurntableTextualApp


def _find_backend(node: ops.Node) -> BaseBackend | None:
    nodes_sources = (ops.DatabaseTable, ops.SQLQueryResult, ops.UnboundTable)
    if isinstance(node, nodes_sources):
        return node.source
    pos_nodes = node.find(nodes_sources)
    if len(pos_nodes) > 0:
        return pos_nodes[0].source

    return None


def _leafs(g: rx.PyDiGraph) -> list[int]:
    return [index for index in g.node_indexes() if g.out_degree(index) == 0]


def _roots(g: rx.PyDiGraph) -> list[int]:
    return [index for index in g.node_indexes() if g.in_degree(index) == 0]


class VinylGraph(rx.PyDiGraph):
    def _leafs(self):
        return _leafs(self)

    def _roots(self):
        return _roots(self)

    @classmethod
    def _new_init_from_expr(cls, expr, label_func=None):
        return VinylGraph._init_from_expr_helper(
            expr.op(), VinylGraph(), {}, label_func
        )

    @staticmethod
    def _init_from_expr_helper(
        u, g: VinylGraph, node_dict: dict[str, int], label_func=None
    ):
        if isinstance(u, ops.Node):
            u_hash = str(u.__hash__())
            if u_hash not in node_dict:
                node_dict[u_hash] = g.add_node(
                    u if label_func is None else label_func(u)
                )
            u_index = node_dict[u_hash]
            for v in u.__children__:
                if isinstance(v, ops.Node):
                    v_hash = str(v.__hash__())
                    if v_hash not in node_dict:
                        node_dict[v_hash] = g.add_node(
                            v if label_func is None else label_func(v)
                        )
                    v_index = node_dict[v_hash]
                    if (u_index, v_index) not in g.edges():
                        g.add_edge(u_index, v_index, 1)
                    g = VinylGraph._init_from_expr_helper(v, g, node_dict, label_func)

        node_dict = {}  # reset to ensure no future issues
        return g

    @staticmethod
    def _find_unaltered_cols(expr) -> dict[ir.Expr, ir.Expr]:
        g = VinylGraph._new_init_from_expr(expr.select(s.all()).tbl)

        # delete edge_to_edge connection
        for u, v in g.edge_list():
            if isinstance(g[u], ops.Relation) and isinstance(g[v], ops.Relation):
                g.remove_edge(u, v)

        # delete final table on either side of the graph:
        for leaf in g._leafs():
            g.remove_node(leaf)

        for root in g._roots():
            g.remove_node(root)

        # store the end nodes of the final table
        columns_to_check = g._leafs()

        # remove the relation nodes and reconnect them to the final table if the column name is the same
        for node in g.node_indexes():
            if isinstance(g[node], ops.Relation):
                frozens = [arg for arg in g[node].args if isinstance(arg, FrozenDict)]
                combined = {}
                for f in frozens:
                    for k, v in f.items():
                        combined[k] = v

                in_nodes = list(g.predecessor_indices(node))
                out_nodes = list(g.successor_indices(node))
                for in_node in in_nodes:
                    for out_node in out_nodes:
                        if combined[g[in_node].name] == g[out_node]:
                            g.add_edge(in_node, out_node, 1)
                g.remove_node(node)

        unaltered = {}
        orig_g = g.copy()
        for col in columns_to_check:
            sub = orig_g.subgraph([col, *rx.ancestors(g, col)])  # type: ignore[attr-defined]
            root = _roots(sub)
            if len(root) > 1:
                continue
            elif all(
                [
                    isinstance(sub[i], (ops.Alias, ops.Field, ops.SortKey))
                    for i in sub.node_indexes()
                ]
            ):
                unbound_tbl, col_name = orig_g[col].args
                unaltered[getattr(unbound_tbl.to_expr(), col_name)] = sub[root[0]]

        return unaltered

    @classmethod
    def _visualize(cls, expr: ir.Expr):
        from netext import ConsoleGraph
        from netext.edge_rendering.arrow_tips import ArrowTip
        from netext.edge_rendering.modes import EdgeSegmentDrawingMode
        from netext.edge_routing.modes import EdgeRoutingMode
        from netext.textual.widget import GraphView

        g_rust = cls._new_init_from_expr(expr, label_func=lambda x: x)
        g = _rustworkx_to_networkx(
            g_rust,
        )

        nx.set_node_attributes(
            g,
            {n: _get_label(n, markup=True) for i, n in enumerate(g.nodes())},
            "$label",
        )

        nx.set_node_attributes(g, lambda n, d, s: d["$label"], "$content-renderer")
        nx.set_edge_attributes(g, EdgeRoutingMode.ORTHOGONAL, "$edge-routing-mode")
        nx.set_edge_attributes(
            g, EdgeSegmentDrawingMode.BOX_ROUNDED, "$edge-segment-drawing-mode"
        )
        nx.set_edge_attributes(g, ArrowTip.ARROW, "$start-arrow-tip")

        if _is_notebook():
            console = Console(
                width=10000
            )  # make width large to avoid jupyter cutting off output
            console.print(ConsoleGraph(g, zoom=1.2, console=console))

        else:

            class GraphviewApp(TurntableTextualApp):
                def compose(self) -> ComposeResult:
                    yield GraphView(g, zoom=1.2)
                    yield Footer()

            GraphviewApp().run()


def _unify_backends(tbl, visited_nodes=set()):
    g = VinylGraph._new_init_from_expr(tbl)
    for i in rx.topological_sort(g):
        node = g[i]
        if node in visited_nodes:
            continue
        visited_nodes.add(node)

        if isinstance(
            node, (ops.JoinChain, ops.Union, ops.Difference, ops.Intersection)
        ):
            if isinstance(node, ops.JoinChain):
                nodes = [node.first.parent]
                nodes.extend([n.table.parent for n in node.rest])
            else:
                nodes = [node.left, node.right]
            sources = [_find_backend(n) for n in nodes]
            non_null_sources = [s for s in sources if s is not None]

            # determine dominant backend
            counted = Counter(sources)
            most_common = counted.most_common()

            # only do replacement if left and right have different sources and neither is a MemTable
            if len(non_null_sources) > 0 and len(set(non_null_sources)) > 1:
                expressions = [n.to_expr() for n in nodes]
                schemas = [n.schema for n in nodes]
                replace = {}

                # if one of the most common sources is duckdb, use that
                if any(
                    [
                        isinstance(n[0], ibis.backends.duckdb.Backend)
                        for n in most_common
                    ]
                ):
                    for i, node in enumerate(nodes):
                        if not isinstance(sources[i], ibis.backends.duckdb.Backend):
                            replace[node] = ibis.memtable(
                                data=expressions[i].to_pyarrow(), schema=schemas[i]
                            ).op()

                # otherwise use the first most common source:
                else:
                    for i, node in enumerate(nodes):
                        if sources[i] != most_common[0][0]:
                            replace[node] = ibis.memtable(
                                data=expressions[i].to_pyarrow(), schema=schemas[i]
                            ).op()

                tbl = tbl.op().replace(replace).to_expr()
                return _unify_backends(tbl, visited_nodes)

    return tbl
