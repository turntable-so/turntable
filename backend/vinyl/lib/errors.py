import json
from enum import Enum
from typing import Any, Callable, Sequence

from sqlglot.dialects.dialect import Dialect

from vinyl.lib.dbt_methods import DBTDialect


class VinylErrorType(str, Enum):
    FILE_NOT_FOUND = "FileNotFoundError"
    DATABASE_ERROR = "DatabaseError"
    OPTIMIZE_ERROR = "OptimizeError"
    PARSE_ERROR = "ParseError"
    CYCLE_ERROR = "CycleError"
    NO_CONTENTS_ERROR = "NoContentsError"
    MISCELLANEOUS_ERROR = "MiscellaneousError"
    NO_LINEAGE_ERROR = "NoLineageError"


class VinylError:
    node_id: str
    source_id: str | None = None
    type: VinylErrorType
    msg: str
    traceback: str | None = None
    dialect: DBTDialect | Dialect | None = None
    context: str | None = None

    def __init__(
        self,
        node_id: str,
        type: VinylErrorType,
        msg: str,
        source_id: str | None = None,
        traceback: str | None = None,
        dialect: DBTDialect | Dialect | None = None,
        context: str | None = None,
    ):
        self.node_id = node_id
        self.source_id = source_id
        self.type = type
        self.msg = msg
        self.traceback = traceback
        self.dialect = dialect
        self.context = context

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "source_id": self.source_id,
            "type": self.type.value,
            "msg": self.msg,
            "traceback": self.traceback,
            "dialect": str(self.dialect),
            "context": self.context,
        }

    def to_json(self):
        return json.dumps(
            {
                "node_id": self.node_id,
                "type": self.type.value,
                "msg": self.msg,
                "traceback": self.traceback,
                # TODO: @justin to fix
                # "dialect": self.dialect.value,
                "context": self.context,
            }
        )

    def attach_context(
        self,
        ast: str,
        func_rules: Sequence[Callable[..., Any]],
    ):
        self.context = ast
