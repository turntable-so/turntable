import functools
import importlib
import inspect
from functools import wraps
from typing import Any, Callable

from vinyl.lib.enums import AssetType
from vinyl.lib.metric import MetricStore
from vinyl.lib.settings import _get_project_module_name
from vinyl.lib.table import VinylTable
from vinyl.lib.utils.functions import _validate


@_validate
def _base(
    deps: object | Callable[..., Any] | list[object | Callable[..., Any]],
    asset_type: AssetType | None = None,
    read_only: bool = False,
    publish: bool = False,
    tags: str | list[str] | None = None,
    description: str | None = None,
    column_descriptions: dict[str, str] | None = None,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            if not isinstance(deps, list):
                deps_adj = [deps]
            else:
                deps_adj = deps
            # Map the positional arguments to the new names
            params = [
                param.name for param in inspect.signature(func).parameters.values()
            ]
            if len(params) != len(deps_adj):
                raise Exception("Wrong number of arguments")

            new_kwargs = {}
            # do dependency injection for each param of the function

            for i, param in enumerate(params):
                if deps_adj[i] is None:
                    continue
                # TODO: this is a hack to avoid mutable sources and models from being impacted downstream
                # we should eventually clean this up as it's not a sustainable solution
                dep_it = deps_adj[i]()
                if isinstance(dep_it, (VinylTable, MetricStore)):
                    par = dep_it._copy()

                else:
                    raise ValueError(
                        f"Dependencies must be VinylTable or MetricStore, not {type(dep_it)}"
                    )

                par._mutable = True
                new_kwargs[param] = par

            return func(**new_kwargs)

        setattr(wrapper, "_module", inspect.getmodule(func).__name__)
        setattr(wrapper, f"_is_vinyl_{asset_type.value}", True)
        if asset_type == AssetType.MODEL or AssetType.METRIC:
            deps_helper = [deps] if not isinstance(deps, list) else deps
            setattr(wrapper, "_deps", deps_helper)
        if tags:
            setattr(wrapper, "_tags", tags)
        if description:
            setattr(wrapper, "_description", description)
        if publish:
            setattr(wrapper, "_publish", publish)

        return wrapper

    return decorator


@_validate
def model(
    deps: object | Callable[..., Any] | list[object | Callable[..., Any]],
    read_only: bool = False,
    publish: bool = False,
    destination: list[str] | None = None,
    tags: str | list[str] | None = None,
    description: str | None = None,
    column_descriptions: dict[str, str] | None = None,
):
    return _base(
        deps=deps,
        asset_type=AssetType.MODEL,
        read_only=read_only,
        publish=publish,
        tags=tags,
        description=description,
        column_descriptions=column_descriptions,
    )


@_validate
def metric(
    deps: object | Callable[..., Any] | list[object | Callable[..., Any]],
    tags: str | list[str] | None = None,
    publish: bool = False,
    description: str | None = None,
    metric_descriptions: dict[str, str] | None = None,
):
    return _base(
        deps=deps,
        asset_type=AssetType.METRIC,
        publish=publish,
        tags=tags,
        description=description,
        column_descriptions=metric_descriptions,
    )


def resource(func: Callable[..., Any], default: bool = False):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        return func(*args, **kwargs)

    decorated_function._is_vinyl_resource = True  # type: ignore
    decorated_function._default = default  # type: ignore

    return decorated_function


def get_resource_by_name(name: str):
    module = importlib.import_module(f"{_get_project_module_name()}.resources")
    return getattr(module, name)
