from collections.abc import Hashable
from typing import Any

import ibis.expr.operations as ops
import networkx as nx
from grandalf.graphs import Edge, Graph, Vertex  # type: ignore
from grandalf.layouts import SugiyamaLayout  # type: ignore
from netext.edge_rendering.arrow_tips import ArrowTip
from netext.edge_rendering.modes import EdgeSegmentDrawingMode
from netext.edge_routing.modes import EdgeRoutingMode
from netext.geometry.point import FloatPoint  # type: ignore
from netext.layout_engines.engine import G, LayoutEngine
from netext.node_rasterizer import JustContent
from netext.textual.widget import GraphView
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import Footer

from vinyl.lib.utils.graphics import TurntableTextualApp, _adjust_type


class GrandalfView:
    w = 0
    h = 0
    xy = (0, 0)


def _create_vertex_horizontal(node: Hashable, data: dict[str, Any]) -> Vertex:
    v = Vertex(node)

    # The API is a bit weird that it assumes to just add some members externally.
    v.view = GrandalfView()
    v.view.h = data["_netext_node_buffer"].layout_width * 5
    v.view.w = data["_netext_node_buffer"].layout_height * 2
    return v


class GrandalfLRSugiyamaLayout(LayoutEngine[G]):
    """Layout engine that uses the grandalf library to layout the graph using the Sugiyama algorithm.

    Multiple components will be placed next to each other.
    """

    def __call__(self, g: G) -> dict[Hashable, FloatPoint]:
        vertices = {
            node: _create_vertex_horizontal(node, data)
            for node, data in g.nodes(data=True)
        }
        edges = [Edge(vertices[u], vertices[v]) for u, v in g.edges]
        graph = Graph(vertices.values(), edges)

        # TODO Open up settings to netext
        for c in graph.components():
            sug = SugiyamaLayout(c)
            sug.init_all()
            sug.draw(3)
        # Rescale back, but leave a bit more space to avoid overlaps in the
        # terminal coordinate space.
        result = dict()
        y_offset = 0
        for c in graph.components():
            component = {
                v.data: FloatPoint(y=v.view.xy[0] / 4 + y_offset, x=v.view.xy[1] / 6)
                for v in c.sV
            }
            y_offset = max([v.view.xy[0] / 4 + y_offset + v.view.w for v in c.sV])
            result.update(component)
        return result


def _render(n, d, s):
    t = Table(title=str(n))
    node = d["node"]

    t.add_column("Name")
    t.add_column("Type")
    t.add_column("Key")

    schema = node.schema()
    types = schema.types

    for i, (name, type) in enumerate(schema.items()):
        field = getattr(node._source_class, name)
        if field.primary_key:
            key = "PK"
            to_bold = True
        elif field.foreign_key is not None:
            source = field.foreign_key.op().find(ops.UnboundTable)[0].name
            col_name = field.foreign_key.get_name()
            key = Text("FK", style="blue") + Text(
                f" {source}.{col_name}", style="white"
            )
            name = Text(name, style="blue")
            to_bold = False
        else:
            key = ""
            to_bold = False

        adj_type = _adjust_type(types[i])

        if to_bold:
            t.add_row(name, adj_type, key, style="on bright_black")
        else:
            t.add_row(name, adj_type, key)

    return t


def create_erd_app(g: nx.DiGraph) -> GraphView:
    nx.set_node_attributes(g, _render, "$content-renderer")
    nx.set_node_attributes(g, JustContent(), "$shape")
    nx.set_edge_attributes(g, EdgeRoutingMode.ORTHOGONAL, "$edge-routing-mode")
    nx.set_edge_attributes(
        g, EdgeSegmentDrawingMode.BOX_ROUNDED, "$edge-segment-drawing-mode"
    )
    nx.set_edge_attributes(g, ArrowTip.ARROW, "$end-arrow-tip")

    class GraphviewApp(TurntableTextualApp):
        def compose(self) -> ComposeResult:
            yield GraphView(g, zoom=1.2, layout_engine=GrandalfLRSugiyamaLayout())
            yield Footer()

    return GraphviewApp()
