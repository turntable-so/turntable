from __future__ import annotations

import os
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from vinyl.lib.settings import _get_project_module_name, _load_project_module
from vinyl.lib.utils.functions import _with_modified_env
from vinyl.lib.utils.graph import DAG
from vinyl.lib.utils.pkg import (
    _find_submodules_names,
)


def _load_project_defs() -> Defs:
    imported_module = _load_project_module()
    return imported_module.defs


def _create_dag_from_model_dict_list(models: list[dict]) -> DAG:
    model_dag = DAG()
    for model_dict in models:
        model_dag.add_node(model_dict["unique_name"])
        for dep in model_dict["config"].get("deps", {}).values():
            model_dag.add_edge(dep, model_dict["unique_name"])
    return model_dag


@dataclass
class Defs:
    resources: list[Any]
    sources: list[Any]
    models: list[Any]
    metrics: list[Any]
    graph: DAG | None
    default_resource: Any

    def __init__(
        self,
        resources=[],
        sources=[],
        models=[],
        metrics=[],
        graph=None,
        default_resource=None,
    ):
        self.resources = resources
        self.sources = sources
        self.models = models
        self.metrics = metrics
        self.graph = DAG() if graph is None else graph
        self.db_graph = DAG()
        self.default_resource = default_resource

    def _process(self, asset):
        metric_nodes = set()
        for key in ["resource", "source", "model", "metric"]:
            plural_key = key + "s"
            if hasattr(asset, f"_is_vinyl_{key}"):
                current = getattr(self, plural_key)
                if asset not in current:
                    setattr(
                        self,
                        plural_key,
                        getattr(self, plural_key) + [asset],
                    )
                if key in ["model", "metric"]:
                    self.graph.add_node(asset)
                    for dep in asset._deps:
                        # if isinstance(dep, VinylTable):
                        #     # use original source class
                        #     dep = dep._source_class
                        self.graph.add_edge(dep, asset)
                    if key == "metric":
                        metric_nodes.add(asset)
                if key in ["resource"]:
                    if asset._default:
                        self.default_resource = asset

    def _post_process(self):
        # remove and reconnect metric nodes for db_graph, since they don't produce actual tables
        self.db_graph = self.graph.copy()
        self.db_graph.remove_nodes_and_reconnect(self.metrics)

    @classmethod
    def load(cls, proj_name: str | None = None, parallel: bool = False) -> Defs:
        def fn(cls):
            defs_instance = Defs()
            if proj_name is not None:
                project_module_name = proj_name
            else:
                project_module_name = _get_project_module_name()
            modules = []
            modules.append(import_module(f"{project_module_name}.resources"))
            modules.append(import_module(f"{project_module_name}.sources"))
            no_models_vinyl = os.getenv("NO_MODELS_VINYL")
            if no_models_vinyl is None or no_models_vinyl == "False":
                modules.append(import_module(f"{project_module_name}.models"))

            for m in modules:
                for name in _find_submodules_names(m):
                    module = import_module(name)
                    for func in dir(module):
                        attr = getattr(module, func)
                        if func != "_":
                            # order here is important, resources, but be imported before sources
                            defs_instance._process(attr)

            defs_instance._post_process()
            return defs_instance

        if parallel:
            # make duckdb read only
            fn = _with_modified_env("DUCKDB_READ_ONLY", "1")(fn)

        return fn(cls)
