from __future__ import annotations

import copy
from typing import Any, Callable, TypeAlias

import ibis
import ibis.common.exceptions as com
import ibis.expr.datatypes as dt
import ibis.expr.operations as ops
import ibis.expr.types as ir
from ibis import _
from ibis import selectors as s
from ibis.common.deferred import Deferred

from vinyl.lib.graph import VinylGraph

base_column_type: TypeAlias = str | ir.Value | Callable[..., Any]

base_boolean_column_type: TypeAlias = ir.BooleanValue | Callable[..., Any]
boolean_column_type: TypeAlias = (
    base_boolean_column_type | list[base_boolean_column_type]
)


column_type_without_dict: TypeAlias = (
    base_column_type | s.Selector | list[base_column_type | s.Selector]
)

column_type: TypeAlias = column_type_without_dict | dict[str, base_column_type]

column_type_all: TypeAlias = column_type_without_dict | list[column_type_without_dict]


# @_validate
def _append_name(col: ir.Value | Deferred, name: str | None = None) -> base_column_type:
    if name is None:
        return col
    try:  # check if v can be named, if it can't, wrap in coalesce
        col_named = col.name(name)
    except Exception:
        col_named = ibis.coalesce(col).name(name)

    return col_named


# @_validate
def _process_cols_arg(
    tbl: ir.Table,
    cols: column_type | None,
    names: list[str | None] | str | None = None,
    passthrough_deferred=False,
) -> list[ir.Value]:
    out: list[ir.Value] = []
    name = names[0] if isinstance(names, list) else names
    if cols is None:
        return [None]

    elif isinstance(cols, ir.Value):
        out = [_append_name(cols, name)]

    elif isinstance(cols, str):
        out = [_append_name(getattr(tbl, cols), name)]

    elif isinstance(cols, Deferred):
        if passthrough_deferred:
            out = [_append_name(cols, name)]
        else:
            out = [_append_name(cols.resolve(tbl), name)]

    elif callable(cols):
        if passthrough_deferred:
            out = [lambda t: _append_name(cols(t), name)]
        else:
            out = [_append_name(cols(tbl), name)]

    elif isinstance(cols, s.Selector):
        out = cols.expand(tbl)

    elif isinstance(cols, list):
        for col in cols:
            out.extend(
                _process_cols_arg(tbl, col, passthrough_deferred=passthrough_deferred)
            )

    elif isinstance(cols, dict):
        for name, col in cols.items():
            out.extend(
                _process_cols_arg(
                    tbl, col, name, passthrough_deferred=passthrough_deferred
                )
            )

    return out


class ColumnBuilder:
    _tbl: ir.Table
    _col: ir.Value | None

    def __init__(
        self,
        tbl: ir.Table,
        col: base_column_type | s.Selector | None,
        passthrough_deferred=False,
    ):
        self._tbl = tbl
        if col is None:
            self._col = col
        else:
            self._col = _process_cols_arg(
                self._tbl, col, passthrough_deferred=passthrough_deferred
            )[0]

    @property
    def _name(self) -> str | None:
        if self._col is None:
            return None

        elif isinstance(self._col, str):
            return self._col

        elif isinstance(self._col, Deferred):
            return self._col.resolve(self._tbl).get_name()

        elif callable(self._col):
            return self._col(self._tbl).get_name()

        return self._col.get_name()

    @property
    def _type(self) -> dt.DataType | None:
        if self._col is None:
            return None

        elif isinstance(self._col, str):
            return getattr(self._tbl, self._col).resolve(self._tbl).type()

        elif isinstance(self._col, Deferred):
            return self._col.resolve(self._tbl).type()

        elif callable(self._col):
            return self._col(self._tbl).type()

        return self._col.type()

    @property
    def _name_as_deferred(self) -> Deferred | None:
        if self._col is None or self._name is None:
            return None
        return getattr(_, self._name)

    def _name_as_deferred_resolved(self, tbl) -> ir.Value | None:
        if self._col is None or self._name is None:
            return None
        col = getattr(tbl, self._name)
        if hasattr(col, "_col"):
            # is VinylColumn
            return col._col
        else:
            # is ibis column
            return col

    @property
    def _lambdaized(self) -> Callable[[ir.Table], ir.Value]:
        if isinstance(self._col, Deferred):
            return self._col.resolve(self._tbl)

        if self._col is None or self._tbl is None:
            return lambda t: None

        if callable(self._col):
            return self._col

        def out(t: ir.Table) -> ir.Value:
            if self._col is None:
                return None
            return self._col.op().replace({self._tbl.op(): t.op()}).to_expr()

        return out

    @property
    def _sources(self) -> list[str] | None:
        if self._col is None:
            return None

        elif isinstance(self._col, Deferred):
            return self._col.resolve(self._tbl)

        elif callable(self._col):
            return self._col(self._tbl)

        return [i.name for i in self._col.op().find_topmost(ops.Field)]

    @property
    def _nodes(self) -> list[ir.Expr]:
        graph = VinylGraph._new_init_from_expr(self._tbl.select(self._col))
        return graph.nodes()

    @property
    def _is_unaltered(self) -> bool:
        allowed = (ops.Field, ops.Relation)
        return all([isinstance(n, allowed) for n in self._nodes])

    @property
    def _is_only_aliased(self) -> bool:
        allowed = (ops.Field, ops.Relation, ops.Alias)
        return all([isinstance(n, allowed) for n in self._nodes])


class ColumnListBuilder:
    _tbl: ir.Table
    _unique: bool
    _cols: list[ColumnBuilder]
    _passthrough_deferred: bool

    def __init__(
        self,
        tbl: ir.Table,
        cols: dict[str, Deferred | ir.Value]
        | list[Deferred | ir.Value | s.Selector]
        | Deferred
        | ir.Value
        | s.Selector
        | None,
        unique: bool = False,
        passthrough_deferred: bool = False,
    ):
        self._tbl = tbl
        self._unique = unique
        self._passthrough_deferred = passthrough_deferred
        self._cols = []

        cols = _process_cols_arg(
            self._tbl, cols, passthrough_deferred=passthrough_deferred
        )
        if cols is None:
            pass
        elif isinstance(cols, list):
            for col in cols:
                if isinstance(col, s.Selector):
                    self._cols.extend(
                        [
                            ColumnBuilder(
                                tbl, c, passthrough_deferred=passthrough_deferred
                            )
                            for c in col.expand(self._tbl)
                        ]
                    )
                else:
                    self._cols.append(
                        ColumnBuilder(
                            tbl, col, passthrough_deferred=passthrough_deferred
                        )
                    )
        else:
            if isinstance(cols, s.Selector):
                self._cols = [
                    ColumnBuilder(tbl, c, passthrough_deferred=passthrough_deferred)
                    for c in cols.expand(self._tbl)
                ]
            else:
                self._cols = [
                    ColumnBuilder(tbl, cols, passthrough_deferred=passthrough_deferred)
                ]

        if unique:
            self._make_unique()

    def __iter__(self):
        return iter(self._cols)

    def __add__(self, other) -> ColumnListBuilder:
        if isinstance(other, ColumnBuilder):
            if self._tbl != other._tbl:
                raise ValueError(
                    "Can only add a VinylColumn to a VinylColumnList from the same VinylTable"
                )
            self._cols.append(other)
            return ColumnListBuilder(
                self._tbl,
                self._cols,
                unique=self._unique,
                passthrough_deferred=self._passthrough_deferred,
            )
        elif not isinstance(other, ColumnListBuilder):
            raise ValueError(
                f"Can only add a VinylColumnList to another VinylColumnList, not a {type(other)}"
            )

        elif self._tbl.__hash__() != other._tbl.__hash__():
            raise ValueError(
                "Can only add a VinylColumnList to another VinylColumnList from the same VinylTable"
            )

        return ColumnListBuilder(
            self._tbl,
            [c._col for c in self._cols] + [c._col for c in other._cols],
            unique=self._unique and other._unique,
            passthrough_deferred=self._passthrough_deferred,
        )

    def __radd__(self, other) -> ColumnListBuilder:
        if isinstance(other, ColumnListBuilder):
            return other.__add__(self)

        return self.__add__(other)

    def _windowize(self, window_, adj_object=False) -> ColumnListBuilder:
        # ensure col can be windowed
        new_obj = self if adj_object else copy.deepcopy(self)
        for col in new_obj._cols:
            if col._col is None:
                continue
            try:
                windowed = col._col.over(window_)
                if isinstance(windowed, Deferred):
                    windowed = windowed.resolve(self._tbl)
                col._col = windowed
            except com.IbisTypeError:
                pass

        return new_obj

    def _make_unique(self) -> None:
        names = []
        unique_cols = []
        zipped = list(zip(self._names, self._queryable))[
            ::-1
        ]  # reverse so latest iteration of column is kept
        for name, col in zipped:
            if name not in names:
                names.append(name)
                unique_cols.append(col)

        unique_cols = unique_cols[::-1]
        self._cols = [
            ColumnBuilder(self._tbl, col, self._passthrough_deferred)
            for col in unique_cols
        ]
        self._unique = True

    def _reset_tbl(self, tbl: ir.Table) -> None:
        self._tbl = tbl

    @property
    def _queryable(self) -> list[ir.Value]:
        out = []
        for col in self._cols:
            if col._col is not None:
                out.append(col._col)
        return out

    @property
    def _lambdaized(self) -> list[Callable[[ir.Table], ir.Value]]:
        return [col._lambdaized for col in self._cols if col._col is not None]

    @property
    def _sources_as_deferred(self) -> list[Deferred]:
        return [getattr(_, col) for col in self._get_direct_col_sources(unique=True)]

    def _sources_as_deferred_resolved(self, tbl) -> list[ir.Value]:
        return [getattr(tbl, col) for col in self._get_direct_col_sources(unique=True)]

    @property
    def _names(self) -> list[str | None]:
        return [col._name for col in self._cols]

    @property
    def _types(self) -> list[dt.DataType | None]:
        return [col._type for col in self._cols]

    @property
    def _names_as_deferred(self) -> list[Deferred | None]:
        return [col._name_as_deferred for col in self._cols]

    def _names_as_deferred_resolved(self, tbl: ir.Table) -> list[ir.Value | None]:
        init = [col._name_as_deferred_resolved(tbl) for col in self._cols]
        return [i for i in init if i is not None]

    def _get_direct_col_sources(self, unique: bool = True) -> list[str]:
        # ibis table, not vinylTable
        col_sources = []
        for col in self._queryable:
            if isinstance(col, Deferred):
                col = col.resolve(self._tbl)
            if callable(col):
                col = col(self._tbl)
            sel_sources = [i.name for i in col.op().find_topmost(ops.Field)]
            if unique:
                col_sources.extend(sel_sources)
            else:
                col_sources.append(sel_sources)

        if unique:
            col_sources = list(set(col_sources))

        return col_sources


class SortColumnListBuilder(ColumnListBuilder):
    _reverse: bool

    def __init__(
        self, tbl, cols, reverse=False, unique=False, passthrough_deferred=False
    ):
        # interpret all sort cols with a - on the outside as descending
        cols = _process_cols_arg(tbl, cols)
        new_cols = []
        for col in cols:
            if col is None:
                new_cols.append(None)
                continue
            col_op = col.op()
            if isinstance(col_op, ops.Negate):
                arg = col_op.args[0]
                new_cols.append(ops.SortKey(arg, ascending=False).to_expr())
            else:
                new_cols.append(col)

        super().__init__(
            tbl, new_cols, unique, passthrough_deferred=passthrough_deferred
        )
        self._reverse = reverse

    @property
    def _sorted(self) -> list[ops.SortKey]:
        final = []
        for so in self._cols:
            # columns can't be None
            if so._col is None:
                continue

            # columns must be resolved for this to work
            if isinstance(so._col, Deferred):
                so._col = so._col.resolve(self._tbl)

            op_it = so._col.op()
            if isinstance(op_it, ops.SortKey):
                # in this case ops_it is a tuple, where the first key is the column and the second is the sort order bool (true is ascending)
                col_expr = op_it.args[0].to_expr()
                out_it = (
                    col_expr.asc() if op_it.args[1] ^ self._reverse else col_expr.desc()
                )
            else:
                out_it = so._col.desc() if self._reverse else so._col.asc()
            final.append(out_it)

        return final

    @property
    def _unsorted(self) -> list[ir.Value]:
        final = []
        for so in self._cols:
            # columns can't be None
            if so._col is None:
                continue

            op_it = so._col.op()
            if isinstance(op_it, ops.SortKey):
                # in this case ops_it is a tuple, where the first key is the column and the second is the sort order bool (true is ascending)
                col_expr = op_it.args[0].to_expr()

            elif isinstance(op_it, ops.Alias) and isinstance(
                op_it.args[0], ops.SortKey
            ):
                col_expr = op_it.args[0].args[0].to_expr().name(op_it.args[1])

            else:
                col_expr = so._col
                # in this case, asc is the default
            final.append(col_expr)

        return final

    @property
    def _names_as_deferred_sorted(self) -> list[Deferred]:
        directions = self._sort_directions
        out = []
        for i, name_def in enumerate(self._names_as_deferred):
            if name_def is None:
                continue
            out.append(name_def.asc() if directions[i] else name_def.desc())
        return out

    def _names_as_deferred_resolved_sorted(self, tbl) -> list[ops.SortKey]:
        directions = self._sort_directions
        out = []
        for i, name_def in enumerate(self._names_as_deferred_resolved(tbl)):
            if name_def is None:
                continue
            out.append(name_def.asc() if directions[i] else name_def.desc())
        return out

    @property
    def _sort_directions(self) -> list[bool]:
        sort_directions = []
        for so in self._cols:
            # columns can't be None
            if so._col is None:
                continue
            op_it = so._col.op()
            if isinstance(op_it, ops.SortKey):
                sort_directions.append(op_it.args[1])
            elif isinstance(op_it, ops.Alias) and isinstance(
                op_it.args[0], ops.SortKey
            ):
                sort_directions.append(op_it.args[0].args[1])
            else:
                sort_directions.append(True)

        return sort_directions


# used for autocomplete for VinylTable and MetricStore classes
class ColumnHelper(
    ir.ArrayColumn,
    ir.BinaryColumn,
    ir.BooleanColumn,
    ir.DecimalColumn,
    ir.FloatingColumn,
    ir.INETColumn,
    ir.IntervalColumn,
    ir.JSONColumn,
    ir.LineStringColumn,
    ir.MACADDRColumn,
    ir.MapColumn,
    ir.MultiLineStringColumn,
    ir.MultiPointColumn,
    ir.MultiPolygonColumn,
    ir.NullColumn,
    ir.PointColumn,
    ir.PolygonColumn,
    ir.StringColumn,
    ir.TimestampColumn,
    ir.IntegerColumn,
    ir.UUIDColumn,
):
    def __init__(self, *args, **kwargs):
        super().__init__(self)
