from __future__ import annotations

import inspect
import uuid
from functools import lru_cache
from typing import Any, Literal

import ibis
from ibis.expr.datatypes import DataType
from pydantic import BaseModel, ConfigDict

import vinyl.lib.connect as vc
from app.core.dbt_methods import DBTDialect
from app.models import Resource
from vinyl.lib.asset import model as model_decorator
from vinyl.lib.asset import resource
from vinyl.lib.connect import _ResourceConnector
from vinyl.lib.definitions import Defs, _create_dag_from_model_dict_list
from vinyl.lib.field import Field  # noqa F401
from vinyl.lib.metric import MetricStore
from vinyl.lib.project import Project
from vinyl.lib.source import source as source_decorator
from vinyl.lib.table import VinylTable
from vinyl.lib.utils.functions import find_enum_arguments
from vinyl.lib.utils.obj import find_all_class_descendants

_obj_helper = object()


class ObjectCache:
    resources: dict[str, Any] = {}
    sources: dict[str, Any] = {}
    models: dict[str, Any] = {}

    @classmethod
    def get(
        cls,
        name: str,
        types: list[Literal["resource", "source", "model"]] = [
            "resource",
            "source",
            "model",
        ],
        default: Any = _obj_helper,
    ):
        if name in cls.resources and "resource" in types:
            return cls.resources[name]
        elif name in cls.sources and "source" in types:
            return cls.sources[name]
        elif name in cls.models and "model" in types:
            return cls.models[name]
        elif default != _obj_helper:
            return default
        else:
            raise ValueError(f"Object {name} not found")


class ResourceObject(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    resource: Resource
    _connector: ibis.BaseBackend | None = None
    _args_dict: dict[str, Any] | None = None
    _profile_contents: dict[str, Any] | None = None

    def __init__(self, **data):
        super().__init__(**data)

        if self.resource.type == "DBT":
            self._connector = vc.DBTConnectorLite
            dialect: DBTDialect = DBTDialect._value2member_map_[
                self.resource.resourcedetails.config.get("dialect")
            ]
            self._profile_contents = (
                self.resource.resourcedetails.get_dbt_profile_contents(
                    self.resource.resourcedetais
                )
            )
            if self.resource.tables is None:
                self.resource.tables = ["*.*.*"]

        else:
            self._connector = getattr(vc, self.resource.type + "Connector")
            self._args_dict = self.resource.config
            if self.resource.tables is not None:
                self._args_dict["tables"] = self.resource.tables

        # find all arguments for connector that are enums
        enum_args = find_enum_arguments(self._connector.__init__)
        for arg, enum in enum_args.items():
            self.resource.config[arg] = enum._value2member_map_[
                self.resource.config[arg]
            ]

    def _get_connector(self) -> _ResourceConnector:
        if self.resource.type == "DBT":
            return self._connector(
                dialect=self.resource.config.get("dialect"),
                profile_contents=self._profile_contents,
                tables=self.resource.tables,
            )
        else:
            return self._connector(**self._args_dict)

    def test_connection(self):
        try:
            self._get_connector()._connect()
            return {"success": "True", "msg": None}
        except Exception as e:
            return {"success": "False", "msg": str(e)}

    def instantiate(self):
        @resource
        def resource_func():
            return self._get_connector()

        if self.repository is not None:
            res_helper = self.repository.id
        else:
            res_helper = self.resource.id
        ObjectCache.resources[res_helper] = resource_func

        resource_func._name_override = self.resource.name
        resource_func._object = self.resource  # for debugging purposes

        return resource_func


class FieldObject(BaseModel):
    name: str
    type: str
    description: str | None = None
    primary_key: bool = False
    unique: bool = False
    foreign_key: tuple[str, str] | None = None
    pii: bool = False

    @staticmethod
    @lru_cache()
    def data_type_helper(type: str):
        return DataType.from_string(type)

    def instantiate(self):
        return Field(
            name=self.name,
            type=self.data_type_helper(self.type),
            description=self.description,
            primary_key=self.primary_key,
            unique=self.unique,
            pii=self.pii,
            foreign_key=self.foreign_key,
        )


class AssetConfig(BaseModel):
    model_config = ConfigDict(extra="allow")  # type: ignore[typeddict-item]


class SourceConfig(AssetConfig):
    table: str | None = None
    path: str | None = None
    database: str | None = None
    table_schema: str | None = (
        None  # special workaround because pydantic uses the schema attribute
    )
    row_count: int | None = None
    col_replace: dict[str, str] = {}
    columns: dict[str, dict[str, str]] = {}


# Common base class for all assets to unify serialization because all assets are stored in the same table
class AssetObject(BaseModel):
    model_config = ConfigDict(extra="allow")  # type: ignore[typeddict-item]
    repository_id: uuid.UUID | None = None
    resource_id: str | None = None
    name: str
    unique_name: str
    type: str
    read_only: bool
    description: str | None = None
    tags: list[str] | None = None
    config: AssetConfig

    """
    Must provide either repository_id or resource_id
    """


class SourceObject(AssetObject):
    type: str = "source"
    read_only: bool = True
    config: SourceConfig

    def instantiate(self):
        class SourceIt:
            pass

        for attr in self.config.__dict__.copy():
            val = getattr(self.config, attr)
            # special workaround because pydantic uses the schema attribute
            if attr == "table_schema" and val is not None:
                setattr(SourceIt, "_schema", val)
                del self.config.__dict__[attr]
            elif attr != "columns" and val is not None:
                setattr(SourceIt, "_" + attr, val)
                del self.config.__dict__[attr]

        setattr(SourceIt, "_unique_name", self.unique_name)
        setattr(SourceIt, "_name", self.name)

        for col, val in self.config.columns.items():
            field_dict = val
            field_dict["name"] = col
            field = FieldObject(**field_dict)
            instantiated = field.instantiate()
            SourceIt.__annotations__[field.name] = instantiated.type
            setattr(SourceIt, field.name, instantiated)
        if self.repository_id is not None:
            res_helper = self.repository_id
        elif self.resource_id is not None:
            res_helper = self.resource_id
        else:
            raise ValueError("Must provide either repository_id or resource_id")
        source_it = source_decorator(ObjectCache.resources[res_helper])(
            SourceIt
        )  # only one resource per source, so this works
        source_it._object = self.model_dump_json()  # for debugging purposes
        ObjectCache.sources[self.unique_name] = source_it
        return source_it


class ModelStep(BaseModel):
    def instantiate(self, *args, **kwargs):
        pass


class MutatingStep(ModelStep):
    input: str

    def instantiate(self, input: str, model: ModelObject):
        pass


class NonMutatingStep(ModelStep):
    output: str

    def instantiate(self, model: ModelObject):
        pass


class ReturnStep(ModelStep):
    input: str

    def instantiate(self, model: ModelObject):
        return model._deps_carryover[self.input]


class SQLStep(NonMutatingStep):
    sql: str | None
    sources: dict[str, str]
    destination: list[str] | None = None
    repository_id: str | None = None

    def instantiate(self, model: ModelObject):
        adj_sources = {}
        for k, v in self.sources.items():
            adj_v = model._deps_carryover.get(v, None)
            if adj_v is not None:
                adj_sources[k] = adj_v

        if any([isinstance(v, MetricStore) for v in adj_sources.values()]):
            raise ValueError(
                "Metrics cannot yet be used as sources for sql params"
            )  # to add feature in the future
        resource = (
            ObjectCache.resources[self.repository_id] if self.repository_id else None
        )
        out = VinylTable.from_sql(
            self.sql,
            sources=adj_sources,
            resource=resource,
            destination=self.destination,
        )  # type: ignore[arg-type] # fixed by raising ValueError

        model._deps_carryover[self.output] = out

        return out


class ModelConfig(AssetConfig):
    publish: bool = False
    deps: dict[str, str]
    steps: list[dict[str, Any]]
    column_descriptions: dict[str, str] | None = None


class ModelObject(AssetObject):
    type: str = "model"
    _subclass_options: dict[str, Any] = {
        k.__name__: k for k in find_all_class_descendants(ModelStep)
    }

    def __init__(self, **data):
        super().__init__(**data)
        self._deps_carryover = {}

    def instantiate(self):
        # * args, ** kwargs is a hack to allow for replacement of the signature later
        adj_deps = {
            k: ObjectCache.get(v, default=None) for k, v in self.config.deps.items()
        }

        def model_func(*args, **kwargs) -> VinylTable | MetricStore:
            adj_deps_activated = {k: v() for k, v in adj_deps.items() if v is not None}
            for dep_name, dep in adj_deps_activated.items():
                self._deps_carryover[dep_name] = dep
            for step in self.config.steps:
                adj_step: ModelStep = self._subclass_options[step["type"] + "Step"](
                    **step
                )
                adj_step.instantiate(model=self)
                if isinstance(adj_step, ReturnStep):
                    return adj_step.instantiate(model=self)
            else:
                raise ValueError("No return step found")

        current_signature = inspect.signature(model_func)
        new_signature = current_signature.replace(
            parameters=[
                inspect.Parameter(k, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                for k in adj_deps
            ]
        )
        model_func.__signature__ = new_signature

        final_model = model_decorator(deps=[v for v in adj_deps.values()])(model_func)
        final_model._unique_name = self.unique_name
        final_model._object = self  # for debugging purposes
        ObjectCache.models[self.unique_name] = final_model
        return final_model


def load_defs_from_dict(defs_dict: dict) -> Defs:
    defs_instance = Defs()
    defs_dict = defs_dict.copy()
    for resource_dict in defs_dict.get("resources", []):
        resource = ResourceObject(**resource_dict)
        defs_instance._process(resource.instantiate())
    for source_dict in defs_dict.get("sources", []):
        if isinstance(source_dict["config"], dict):
            source_dict["config"] = SourceConfig(**source_dict["config"])
        source = SourceObject(**source_dict)
        defs_instance._process(source.instantiate())

    # load models, ensuring correct import order
    models = defs_dict.get("models", [])
    model_dag = _create_dag_from_model_dict_list(models)
    model_sort_helper = model_dag.topological_sort()
    models = sorted(models, key=lambda x: model_sort_helper.index(x["unique_name"]))
    for model_dict in models:
        if isinstance(model_dict["config"], dict):
            model_dict["config"] = ModelConfig(**model_dict["config"])
        model = ModelObject(**model_dict)
        defs_instance._process(model.instantiate())

    defs_instance._post_process()
    return defs_instance


def bootstrap_project_from_dict(defs_dict: dict) -> Project:
    defs = load_defs_from_dict(defs_dict)
    return Project.load(defs)
