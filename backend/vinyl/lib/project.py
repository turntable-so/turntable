from __future__ import annotations

import dataclasses
import traceback
from typing import Any, Callable

import ibis.expr.types as ir
from mpire import WorkerPool
from rich.table import Table
from sqlglot import exp
from sqlglot.errors import ParseError
from tqdm import tqdm

from vinyl.lib.connect import SourceInfo, _ResourceConnector
from vinyl.lib.definitions import Defs, _load_project_defs
from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.metric import MetricStore
from vinyl.lib.sqlast import SQLAstNode, SQLProject
from vinyl.lib.table import VinylTable
from vinyl.lib.utils.graph import DAG
from vinyl.lib.utils.graphics import rich_print


@dataclasses.dataclass
class Resource:
    name: str
    connector: _ResourceConnector
    def_: Any


class Project:
    resources: list[Resource]
    sources: list[ir.Table]
    models: list[Callable[..., Any]]
    metrics: list[Callable[..., Any]]
    graph: DAG
    db_graph: DAG
    default_resource: Resource

    def __init__(
        self,
        resources: list[Callable[..., Any]],
        sources: list[ir.Table] | None = None,
        models: list[Callable[..., Any]] | None = None,
        metrics: list[Callable[..., Any]] | None = None,
        graph: DAG | None = None,
        db_graph: DAG | None = None,
        default_resource: Resource | None = None,
    ):
        self.resources = [
            Resource(
                name=getattr(resource_def, "_name_override", resource_def.__name__),
                def_=resource_def,
                connector=resource_def(),
            )
            for resource_def in resources
        ]
        if sources is not None:
            self.sources = sources
        if models is not None:
            self.models = models
        if metrics is not None:
            self.metrics = metrics

        self.graph = DAG() if graph is None else graph
        self.db_graph = DAG() if db_graph is None else db_graph
        self.default_resource = (
            self.resources[0] if default_resource is None else default_resource
        )

    def _get_source_objects(self, with_schema=False) -> list[SourceInfo]:
        sources = []
        errors = []
        for resource in self.resources:
            try:
                resource_sources, errors_it = resource.connector._list_sources(
                    with_schema
                )
                for source in resource_sources:
                    source._parent_resource = resource
                    sources.append(source)
                errors.extend(errors_it)
            except Exception as e:
                print(f"Error loading sources from {resource.name}: {e}")
                errors.append(
                    VinylError(
                        resource.name,
                        type=VinylErrorType.DATABASE_ERROR,
                        msg=str(e),
                        traceback=traceback.format_exc(),
                    )
                )
        return sources, errors

    def _get_resource(self, resource_name: str) -> Resource:
        resources = [
            resource for resource in self.resources if resource.name == resource_name
        ]

        if len(resources) == 0:
            raise ValueError(f"Resource {resource_name} not found")

        resource = resources[0]

        return resource

    def _get_source(self, source_id: str):
        sources = [source for source in self.sources if source.__name__ == source_id]

        if len(sources) == 0:
            raise ValueError(f"Source {source_id} not found")

        source = sources[0]

        return source

    def _get_model(self, model_id: str) -> VinylTable:
        if self.models is None:
            raise ValueError("No models found")
        models = [model for model in self.models if model.__name__ == model_id]

        if len(models) == 0:
            raise ValueError(f"Model {model_id} not found")

        model = models[0]

        return model()

    def _get_metric_store(self, metric_id: str) -> MetricStore:
        metrics = [metric for metric in self.metrics if metric.__name__ == metric_id]
        if len(metrics) == 0:
            raise ValueError(f"Metric {metric_id} not found")

        metric = metrics[0]

        return metric()

    def _select_lineage_nodes(
        self,
        ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
    ):
        if ids is None:
            nodes = self.db_graph.topological_sort()
        else:
            node_id_map = {
                VinylTable.get_adj_node_name(n): n
                for n in self.graph.node_dict
                if n is not None
            }
            nodes_to_consider = [node_id_map[id] for id in ids]
            all_nodes_to_consider = self.db_graph.get_ancestors_and_descendants(
                nodes_to_consider, predecessor_depth, successor_depth
            )
            nodes = self.db_graph.subgraph(
                list(all_nodes_to_consider)
            ).topological_sort()

        nodes = [
            n for n in nodes if not isinstance(n, VinylTable)
        ]  # remove source nodes from lineage calc

        return nodes

    def get_sql_project(
        self,
        ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
        calculate_lineage: bool = True,
        parallel: bool = False,
    ):
        nodes = self._select_lineage_nodes(ids, predecessor_depth, successor_depth)

        def process_node(shared_objects, node):
            graph = shared_objects[0]
            sqlnode = SQLAstNode()
            try:
                sqlnode.id = VinylTable.get_adj_node_name(node)
                relative_to = {}
                for y in graph.get_parents([node]):
                    if y is None:
                        continue

                    try:
                        y_name = VinylTable.get_adj_node_name(y)
                        active_y = y()
                        relative_to[y_name] = active_y
                    except Exception as e:
                        sqlnode.errors.append(
                            VinylError(
                                node_id=sqlnode.id,
                                source_id=VinylTable.get_adj_node_name(y),
                                msg=str(e),
                                type=VinylErrorType.MISCELLANEOUS_ERROR,
                                traceback=traceback.format_exc(),
                            )
                        )
                        # don't fail here, fail later if there are no deps to be found. Swallowing the exception allows for partial lineage
                        continue
                sqlnode.ast, sqlnode.schema, sqlnode.dialect = node()._to_sql_ast(
                    relative_to=relative_to,
                    node_name=VinylTable.get_adj_node_name(node),
                )
                sqlnode.deps = [k for k in relative_to]
                sqlnode.deps_schemas = {
                    exp.Table(this=exp.Identifier(this=k)): v.schema()
                    for k, v in relative_to.items()
                }

            except Exception as e:
                sqlnode.errors.append(
                    VinylError(
                        node_id=sqlnode.id,
                        type=(
                            VinylErrorType.PARSE_ERROR
                            if isinstance(e, ParseError)
                            else VinylErrorType.MISCELLANEOUS_ERROR
                        ),
                        dialect=sqlnode.dialect,
                        msg=str(e),
                        traceback=traceback.format_exc(),
                        context=str(node),
                    )
                )
            return sqlnode

        if parallel:
            with WorkerPool(
                n_jobs=min(5, len(nodes)),
                use_dill=True,
                start_method="spawn",
                shared_objects=[self.db_graph],
                keep_alive=True,
            ) as pool:
                sqlnodelist = pool.map(process_node, nodes, progress_bar=True)
        else:
            sqlnodelist = [process_node([self.db_graph], node) for node in tqdm(nodes)]

        adj_db_graph = self.db_graph.copy().relabel(
            lambda x: VinylTable.get_adj_node_name(x) if x is not None else x
        )

        return SQLProject(sqlnodelist, adj_db_graph)

    def list_sources(self, tables: bool = False):
        table = Table("Name", "Resource", "Location", title="Sources")
        for source in self._get_source_objects()[0]:
            if source._parent_resource is None:
                raise ValueError("Source must have a parent resource.")
            table.add_row(
                f"[bold]{source._name}[bold]",
                f"[grey70]{source._parent_resource.def_.__name__}[grey70]",
                f"[grey70]{source._location}[grey70]",
            )
        rich_print(table)

    @classmethod
    def load(cls, defs: Defs) -> Project:
        return cls(
            resources=defs.resources,
            sources=defs.sources,
            models=defs.models,
            metrics=defs.metrics,
            graph=defs.graph,
            db_graph=defs.db_graph,
            default_resource=defs.default_resource,
        )

    @classmethod
    def bootstrap(cls) -> Project:
        defs = _load_project_defs()
        return cls.load(defs)
