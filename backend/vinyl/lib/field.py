from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
from types import ModuleType
from typing import Any

import ibis.expr.operations as ops
import ibis.expr.types as ir
import networkx as nx
import rustworkx as rx
from ibis.expr.datatypes import DataType
from vinyl.lib.column import _demote_arg
from vinyl.lib.utils.graph import _rustworkx_to_networkx
from vinyl.lib.utils.obj import table_to_python_class


def get_caller_module(back: int) -> ModuleType | None:
    frame = inspect.currentframe()
    for _ in range(back + 1):
        if frame is None:
            raise ValueError("Unable to find the module path for the current project")
        frame = frame.f_back
    return inspect.getmodule(frame)


class Field:
    _relations: rx.PyDiGraph = rx.PyDiGraph()
    _relations_node_dict: dict[str, int] = {}
    _source_class_dict: dict[ir.Table, Any] = {}
    _source_adj_tbl_dict: dict[str, Any] = {}  # will be VinylTable
    name: str | None
    type: DataType | None
    description: str | None
    unique: bool
    primary_key: bool
    foreign_key: Field | tuple[str, str] | None
    pii: bool
    _parent_name: str | None
    _parent_ibis_table: object | None
    _parent_vinyl_table: object | None

    def __init__(
        self,
        name: str | None = None,
        type: DataType | None = None,
        description: str | None = None,
        primary_key: bool = False,
        foreign_key: Field | None = None,
        unique: bool = False,
        pii: bool = False,
        parent_name: str | None = None,
        parent_ibis_table: ops.UnboundTable | None = None,
        parent_vinyl_table: Any | None = None,
    ):
        self._parent_name = parent_name
        self._parent_ibis_table = parent_ibis_table
        self._parent_vinyl_table = parent_vinyl_table
        self.name = name
        self.type = type
        self.description = description
        self.primary_key = primary_key
        self.unique = unique
        self.pii = pii
        self.foreign_key = self.process_foreign_key(foreign_key)

    def process_foreign_key(self, foreign_key):
        if foreign_key is None:
            return None

        elif isinstance(foreign_key, tuple):
            if "." not in foreign_key[0]:
                caller_module = get_caller_module(2)
                if caller_module is not None:
                    module_name = caller_module.__name__
                else:
                    raise ValueError(
                        "Unable to find the module path for the current project"
                    )
                parent_module_name = ".".join(module_name.split(".")[:-1])
                parent_module = importlib.import_module(parent_module_name)
                child_modules = []
                for finder, name, ispkg in pkgutil.iter_modules(
                    parent_module.__path__, parent_module_name + "."
                ):
                    child_modules.append(name)

                relevant_names = [
                    name
                    for name in child_modules
                    if table_to_python_class(name.split(".")[-1]) == foreign_key[0]
                ]
                if len(relevant_names) > 1:
                    raise ValueError(
                        f"Multiple classes with the name {foreign_key[0]} found in the parent module. Please specify the full module path."
                    )
                elif len(relevant_names) == 0:
                    raise ValueError(
                        f"No class with the name {foreign_key[0]} found in the parent module."
                    )
                else:
                    adj_module_helper = relevant_names[0], foreign_key[0]

            else:
                split_ = foreign_key[0].split(".")
                adj_module_helper = ".".join(split_[:-1]), split_[-1]

            relevant_module = importlib.import_module(adj_module_helper[0])
            try:
                cls = getattr(relevant_module, adj_module_helper[1])
                foreign_key = getattr(cls, foreign_key[1])
            except AttributeError:
                # ignore fk in case of circular imports or invalid column names
                return None
        elif isinstance(foreign_key, str):
            # get field from str
            field_as_list = foreign_key.split(".")
            modname = ".".join(field_as_list[:-2])
            clsname = field_as_list[-2]
            colname = field_as_list[-1]
            mod = importlib.import_module(modname)
            try:
                cls = getattr(mod, clsname)
                foreign_key = getattr(cls, colname)

            except AttributeError:
                # ignore fk in case of circular imports or invalid column names
                return None

        return _demote_arg(
            foreign_key
        )  # necessary because unprocessed foreign key may be VinylColumn, not Ibis Column

    def _update_source_class(self):
        self._source_class_dict[self._parent_vinyl_table] = (
            self._parent_vinyl_table._source_class
            if hasattr(self._parent_vinyl_table, "_source_class")
            else None
        )

    def _store_source_adj_tbl(
        self, vinyl_tbl: Any
    ):  # will be VinylTable, but can't state due to circular import
        hash_ = str(hash(self._parent_ibis_table))
        if hash_ not in self._source_adj_tbl_dict:
            self._source_adj_tbl_dict[hash_] = vinyl_tbl

    def _store_relations(self):
        self_parent_table_vinyl = self._source_adj_tbl_dict[
            str(hash(self._parent_ibis_table))
        ]
        self._add_node(self_parent_table_vinyl)
        if self.foreign_key is not None:
            foreign_key_op = self.foreign_key.op()
            # note for below, foriegn key class has been imported, so self.foreign_key is an ibis expression at this point
            foreign_key_parent_table_ibis = foreign_key_op.find(ops.UnboundTable)[
                0
            ].to_expr()
            foreign_key_name = foreign_key_op.args[-1]
            foreign_key_parent_table_vinyl = self._source_adj_tbl_dict[
                str(hash(foreign_key_parent_table_ibis))
            ]

            self._add_edge(
                foreign_key_parent_table_vinyl,
                self_parent_table_vinyl,
                (foreign_key_name, self.name),
            )

            if self.unique:
                # relationship is bidirectional, so we need to add the edge in both directions
                self._add_edge(
                    self_parent_table_vinyl,
                    foreign_key_parent_table_vinyl,
                    (self.name, foreign_key_name),
                )

    def _add_node(self, node: ir.Expr):
        hash_ = str(hash(node))
        if hash_ not in self._relations_node_dict:
            self._relations_node_dict[hash_] = self._relations.add_node(node)

    def _add_edge(
        self,
        node1: ir.Expr,
        node2: ir.Expr,
        data: Any,
    ):
        for node in [node1, node2]:
            self._add_node(node)

        self._relations.add_edge(
            self._relations_node_dict[str(hash(node1))],
            self._relations_node_dict[str(hash(node2))],
            data,
        )

    def asdict(self):
        out = {}
        for k, v in self.__dict__.items():
            if v is not None and not k.startswith("_"):
                out[k] = v

        return out

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def _export_relations_to_networkx(
        cls, shorten_name: bool = True, filter: list[str] | None = None
    ) -> nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph:
        G = _rustworkx_to_networkx(cls._relations)
        # make sure node object is passed as data rather than name to prevent issues with renderer
        nx.set_node_attributes(G, {node: node for node in G.nodes()}, "node")

        if shorten_name or filter:
            nx.relabel_nodes(
                G, {node: node.get_name() for node in G.nodes()}, copy=False
            )

        if not filter:
            return G
        else:
            all_nodes = list(G.nodes())
            nodes_in_subgraph: set[str] = set()
            for fil in filter:
                regex = re.compile(fil)
                nodes_to_add = set(node for node in all_nodes if regex.search(node))
                nodes_in_subgraph = nodes_in_subgraph.union(nodes_to_add)

            return G.subgraph(nodes_in_subgraph)

    @classmethod
    def get(cls, base_col: ir.Value):
        op = base_col.op()
        source_tbl = op.args[0].to_expr()
        source_vinyl_table = Field._source_adj_tbl_dict[str(hash(source_tbl))]
        source_vinyl_class = source_vinyl_table._source_class
        return source_vinyl_class._unique_name, getattr(source_vinyl_class, op.args[1])
