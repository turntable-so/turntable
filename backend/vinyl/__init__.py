from __future__ import annotations

import builtins  # noqa: F401
import os

import ibis
import ibis.expr.datatypes as types  # noqa: F401
import pydantic
import sqlglot
from ibis.expr.datatypes import *  # noqa: F401
from rich.traceback import install

from vinyl.lib.asset import (  # noqa: F401
    metric,
    model,
    resource,  # noqa: F401
)

# from vinyl.lib.definitions import Defs  # noqa: F401
from vinyl.lib.enums import FillOptions  # noqa: F401,
from vinyl.lib.env import load_dotenv  # noqa: F401
from vinyl.lib.field import Field  # noqa: F401
from vinyl.lib.metric import MetricStore  # noqa: F401
from vinyl.lib.set import difference, intersect, join, union  # noqa: F401
from vinyl.lib.source import source  # noqa: F401
from vinyl.lib.table import (
    VinylTable,  # noqa: F401
)
from vinyl.lib.utils.graphics import rich_print  # noqa: F401

__all__ = [
    "Field",
    "MetricStore",
    "VinylTable",
    "difference",
    "intersect",
    "join",
    "union",
    "Defs",
    "M",
    "T",
    "rich_print",
    "model",
    "resource",
    "source",
    "FillOptions",
    "types",
    "join",
]

install(
    suppress=[ibis, sqlglot, pydantic],
)


class M(MetricStore):  # noqa: F821
    pass


class T(VinylTable):  # noqa: F821
    pass


original_print = builtins.print  # type: ignore
builtins.print = rich_print  # type: ignore
