from __future__ import annotations

import contextlib
import itertools
from typing import Any, Callable

import deepmerge
import ibis
import ibis.common.exceptions as com
import ibis.expr.operations as ops
import ibis.expr.types as ir
import networkx as nx
import rustworkx as rx
from bidict import bidict
from rich.markup import escape
from rich.text import Text
from rustworkx.visit import DFSVisitor, PruneSearch
from textual.app import ComposeResult
from textual.widgets import Footer

from vinyl.lib.utils.collection import list_union
from vinyl.lib.utils.graphics import TurntableTextualApp, _adjust_type


## Note: outside of DAG class elsewhere, use `to_networkx()` for DAG to avoid errors
def _rustworkx_to_networkx(
    graph: rx.PyDiGraph,
    pre_convert: Callable[..., Any] | None = None,
    post_convert: Callable[..., Any] | None = None,
) -> nx.DiGraph:
    """
    Converts a rustworkx graph to a networkx graph.
    """

    g = nx.DiGraph()
    cur_nodes = graph.nodes()
    if pre_convert is not None:
        cur_nodes = [pre_convert(i) for i in cur_nodes]
    cur_edges = [(cur_nodes[u], cur_nodes[v]) for u, v in graph.edge_list()]
    cur_edge_values = [graph.get_edge_data(u, v) for u, v in graph.edge_list()]
    g.add_nodes_from(nodes_for_adding=cur_nodes)
    for i, edge in enumerate(cur_edges):
        g.add_edge(edge[0], edge[1], cur_edge_values[i])

    if post_convert is not None:
        nx.relabel_nodes(g, post_convert, copy=False)
    return g


## NOTE: Made an attempt at a fix here, but need to verify. Necessary because ops.Join is no longer a valid class
def _get_type(node: ir.Expr) -> Text:
    with contextlib.suppress(AttributeError, NotImplementedError):
        return _adjust_type(node.dtype)

    try:
        schema = node.schema
    except (AttributeError, NotImplementedError):
        # TODO(kszucs): this branch should be removed
        try:
            # As a last resort try get the name of the output_type class
            return node.output_type.__name__
        except (AttributeError, NotImplementedError):
            return Text("\u2205")  # empty set character
    except com.IbisError:
        assert isinstance(node, ops.JoinChain)
        tables = [node.first.parent]
        tables.extend([n.table.parent for n in node.rest])
        table_names = [getattr(t, "name", None) for t in tables]
        schemas = [t.schema for t in tables]
        pairs: list[tuple[str, str]] = []
        for i, table in enumerate(tables):
            pairs.extend(
                (f"{table_names[i]}.{column}", type)
                for column, type in schemas[i].items()
            )
        schema = ibis.schema(pairs)

    out = Text("\n   ")
    len_loop = len(schema.names)
    for i, (name, type) in enumerate(zip(schema.names, schema.types)):
        out += Text(escape(name), style="italic") + Text(": ") + _adjust_type(type)
        if i < len_loop - 1:
            out += Text("\n   ")

    return out


def _get_label(node: ir.Expr, markup=True) -> Text | str:
    typename = _get_type(node)  # Already an escaped string
    name = type(node).__name__
    nodename = (
        node.name
        if isinstance(
            node,
            (
                ops.Literal,
                ops.Field,
                ops.Alias,
                ops.PhysicalTable,
                ops.RangeWindowFrame,
            ),
        )
        else None
    )
    if nodename is not None:
        # [TODO] Don't show nodename because it's too long and ruins the image
        if isinstance(node, ops.window.RangeWindowFrame):
            label = Text(escape(name), style="bold")
        else:
            label = (
                Text(escape(nodename), style="italic")
                + Text(": ")
                + Text(escape(name), style="bold")
            )

            if isinstance(node, ops.Relation):
                label += typename
            else:
                label += Text("\n   :: ") + typename

    else:
        label = Text(escape(name), style="bold")
        if isinstance(node, ops.Relation):
            label += typename
        else:
            label += Text("\n   :: ") + typename
    if markup:
        return label.markup
    return label


class SuccessorVisitor(DFSVisitor):
    def __init__(self, source, depth_limit: int | None = None):
        self.edges: Any = []
        self.degrees = {node: 0 for node in source}
        self.depth_limit = depth_limit

    def tree_edge(self, edge):
        self.edges.append(edge)
        new_degree = self.degrees.get(edge[0]) + 1
        self.degrees[edge[1]] = new_degree
        if new_degree == self.depth_limit:
            raise PruneSearch()


class DAG:
    g: rx.PyDiGraph
    node_dict: bidict[Any, int]

    def __init__(self):
        self.g = rx.PyDiGraph()
        self.node_dict = bidict({})

    def add_node(self, node: Any):
        if node not in self.node_dict:
            p = self.g.add_node(node)
            self.node_dict[node] = p
        return self.node_dict[node]

    def add_edge(self, parent: Any, child: Any, edge: dict[Any, Any] = {}):
        if parent not in self.node_dict:
            self.add_node(parent)
        if child not in self.node_dict:
            self.add_node(child)

        pi = self.node_dict[parent]
        ci = self.node_dict[child]

        if (pi, ci) not in self.g.edge_list():
            parent_node = self.node_dict[parent]
            child_node = self.node_dict[child]
            if parent_node != child_node:
                self.g.add_edge(self.node_dict[parent], self.node_dict[child], edge)
        elif edge is not None:
            old_edge_contents = self.g.get_edge_data(pi, ci)
            if old_edge_contents is None:
                new_edge = deepmerge.always_merger.merge(old_edge_contents, edge)
            else:
                new_edge = edge
            self.g.update_edge(pi, ci, new_edge)

    def get_parents(
        self,
        sources: Any,
    ):
        indexes = [self.node_dict[n] for n in sources]
        out = []
        for i in indexes:
            out.extend(self.g.predecessors(i))

        return list(set(out))

    def get_relatives(
        self,
        sources: Any,
        depth: int | None = None,
        reverse: bool = False,
        include_sources: bool = True,
    ):
        if depth == 0:
            return sources if include_sources else []
        indexes = [self.node_dict[n] for n in sources]
        copy = self.g.copy()
        if reverse:
            copy.reverse()
        g_func = copy if reverse else self.g

        vis = SuccessorVisitor(indexes, depth)
        rx.dfs_search(g_func, indexes, vis)  # type: ignore [attr-defined]
        final_indexes = [k for k, v in vis.degrees.items() if v != 0 or include_sources]
        return [self.node_dict.inv[k] for k in final_indexes]

    def get_ancestors_and_descendants(
        self,
        sources: Any,
        predecessor_depth: int | None,
        successor_depth: int | None,
        include_sources: bool = True,
    ):
        ancestors = self.get_relatives(
            sources, predecessor_depth, reverse=True, include_sources=include_sources
        )
        descendants = self.get_relatives(
            sources, successor_depth, include_sources=include_sources
        )
        return list(set(ancestors + descendants))

    def find_cycles(self):
        for cycle in rx.simple_cycles(self.g):
            yield [self.node_dict.inv[i] for i in cycle]

    def remove_nodes_and_reconnect(
        self, nodes: list[Any], merge_edge_data: bool = True
    ):
        indexes = [
            n
            for n in self.topological_sort(return_indices=True)
            if self.node_dict.inv[n] in nodes
        ]
        for i in indexes:
            sources = [k for k in self.g.predecessor_indices(i)]
            targets = [k for k in self.g.successor_indices(i)]
            new_edges = list(itertools.product(sources, targets))
            new_edges = [
                (source, target) for source, target in new_edges if source != target
            ]  # remove self-loops

            for source, target in new_edges:
                source_val = self.node_dict.inv[source]
                target_val = self.node_dict.inv[target]
                if merge_edge_data:
                    # Preserve ntypes from A -> B and B -> C when removing node B
                    data_A_B = self.g.get_edge_data(source, i)
                    data_B_C = self.g.get_edge_data(i, target)
                    data_A_C = deepmerge.always_merger.merge(data_A_B, data_B_C)
                    self.add_edge(
                        source_val, target_val, data_A_C
                    )  # merges if edge currently exists
                else:
                    self.add_edge(source_val, target_val)
            self.g.remove_node(i)
            del self.node_dict.inv[i]
        return self.g

    def topological_sort(self, return_indices: bool = False):
        indices = rx.topological_sort(self.g)  # type: ignore [attr-defined]
        if return_indices:
            return indices
        return [self.node_dict.inv[i] for i in indices]

    def subgraph(self, nodes: list[Any]):
        out = DAG()
        out.g = self.g.subgraph([self.node_dict[n] for n in nodes])
        out.node_dict = bidict({v: i for i, v in enumerate(out.g.nodes())})

        return out

    def copy(self) -> DAG:
        new = DAG()
        new.g = self.g.copy()
        new.node_dict = self.node_dict.copy()
        return new

    def to_networkx(self) -> nx.DiGraph:
        g = nx.DiGraph()
        cur_nodes = self.g.nodes()
        edge_list = self.g.edge_list()
        cur_edges = [
            (self.node_dict.inv[u], self.node_dict.inv[v]) for u, v in edge_list
        ]
        cur_edge_values = [self.g.get_edge_data(u, v) for u, v in edge_list]
        g.add_nodes_from(nodes_for_adding=cur_nodes)
        for i, edge in enumerate(cur_edges):
            g.add_edge(edge[0], edge[1], **cur_edge_values[i])

        return g

    def get_node_link_json(self) -> str:
        return nx.node_link_data(self.to_networkx())

    def relabel(self, label_func: Callable[..., Any]) -> DAG:
        cur_edges = self.get_edge_tuples()
        cur_edge_values = [self.g.get_edge_data(u, v) for u, v in self.g.edge_list()]
        new = DAG()
        cur_nodes = self.g.nodes()
        for node in cur_nodes:
            new.add_node(label_func(node))
        for i, edge in enumerate(cur_edges):
            new.add_edge(label_func(edge[0]), label_func(edge[1]), cur_edge_values[i])
        self = new
        return self

    def reverse(self):
        self.g.reverse()
        return self

    def get_edge_tuples(self):
        return [
            (self.node_dict.inv[u], self.node_dict.inv[v])
            for u, v in self.g.edge_list()
        ]

    def get_roots(self):
        return [
            self.node_dict.inv[i]
            for i in self.g.node_indexes()
            if self.g.in_degree(i) == 0
        ]

    def get_leaves(self):
        return [
            self.node_dict.inv[i]
            for i in self.g.node_indexes()
            if self.g.out_degree(i) == 0
        ]

    def get_ancestors(self, nodes: list[Any]):
        indexes = [self.node_dict[n] for n in nodes]
        out = []
        for i in indexes:
            ancestor_indexes = rx.ancestors(self.g, i)
            out.extend([self.node_dict.inv[k] for k in ancestor_indexes])
        return list(set(out))

    def get_ancestor_roots(self, nodes: list[Any]):
        return list(set(self.get_ancestors(nodes)) & set(self.get_roots()))

    def visualize(self):
        from netext import ConsoleGraph
        from netext.edge_rendering.arrow_tips import ArrowTip
        from netext.edge_rendering.modes import EdgeSegmentDrawingMode
        from netext.edge_routing.modes import EdgeRoutingMode
        from netext.textual.widget import GraphView

        g = self.to_networkx()

        nx.set_node_attributes(
            g,
            {n: n for i, n in enumerate(g.nodes())},
            "$label",
        )

        nx.set_node_attributes(g, lambda n, d, s: d["$label"], "$content-renderer")
        nx.set_edge_attributes(g, EdgeRoutingMode.ORTHOGONAL, "$edge-routing-mode")
        nx.set_edge_attributes(
            g, EdgeSegmentDrawingMode.BOX_ROUNDED, "$edge-segment-drawing-mode"
        )
        nx.set_edge_attributes(g, ArrowTip.ARROW, "$start-arrow-tip")

        if False:
            # console = Console(
            #     width=1000
            # )  # make width large to avoid jupyter cutting off output
            # console.print(ConsoleGraph(g, zoom=1.2, console=console))
            print(ConsoleGraph(g, zoom=1.2))

        else:

            class GraphviewApp(TurntableTextualApp):
                def compose(self) -> ComposeResult:
                    yield GraphView(g)
                    yield Footer()

            GraphviewApp().run()


def nx_remove_node_and_reconnect(
    g: nx.DiGraph, node: str, preserve_ntype: bool = False
) -> nx.DiGraph:
    if g.is_directed():
        sources = [source for source, _ in g.in_edges(node)]
        targets = [target for _, target in g.out_edges(node)]
    else:
        sources = list(g.neighbors(node))
        targets = sources

    new_edges = list(itertools.product(sources, targets))
    new_edges = [
        (source, target) for source, target in new_edges if source != target
    ]  # remove self-loops

    if preserve_ntype:
        for source, target in new_edges:
            # Preserve ntypes from A -> B and B -> C when removing node B
            ntype_A_B = g.edges[source, node]["ntype"]
            ntype_B_C = g.edges[node, target]["ntype"]
            ntype_A_C = list_union(ntype_A_B, ntype_B_C)
            if g.has_edge(source, target):
                ntype_A_C = list_union(g.edges[source, target]["ntype"], ntype_A_C)
            else:
                g.add_edge(source, target)
            g.edges[source, target]["ntype"] = ntype_A_C
    else:
        g.add_edges_from(new_edges)
    g.remove_node(node)
    return g
