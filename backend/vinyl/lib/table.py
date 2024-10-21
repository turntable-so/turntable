from __future__ import annotations

import gc
import inspect
import os
import pickle as pkl
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

import ibis
import ibis.backends
import ibis.backends.bigquery
import ibis.common.exceptions as com
import ibis.expr.datatypes as dt
import ibis.expr.operations as ops
import ibis.expr.rewrites as rw
import ibis.expr.types as ir
import ibis.selectors as s
from ibis import Schema, _
from ibis import literal as lit
from ibis.backends.bigquery import Backend as BigqueryBackend
from ibis.expr.types.pretty import to_rich
from sqlglot import exp
from sqlglot.optimizer import optimize
from sqlglot.optimizer.eliminate_ctes import eliminate_ctes
from sqlglot.optimizer.eliminate_joins import eliminate_joins
from sqlglot.optimizer.eliminate_subqueries import eliminate_subqueries
from sqlglot.optimizer.normalize import normalize
from sqlglot.optimizer.pushdown_predicates import pushdown_predicates
from sqlglot.optimizer.pushdown_projections import pushdown_projections
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.qualify_columns import validate_qualify_columns
from sqlglot.optimizer.unnest_subqueries import unnest_subqueries

from vinyl.lib.column import VinylColumn, _demote_args
from vinyl.lib.column_methods import (
    ColumnBuilder,
    ColumnListBuilder,
    SortColumnListBuilder,
    base_boolean_column_type,
    base_column_type,
    boolean_column_type,
    column_type,
    column_type_all,
    column_type_without_dict,
)
from vinyl.lib.enums import FillOptions, WindowType
from vinyl.lib.field import Field  # noqa: F401
from vinyl.lib.graph import VinylGraph, _unify_backends
from vinyl.lib.schema import VinylSchema
from vinyl.lib.set_methods import _auto_join_helper, _convert_auto_join_to_ibis_join
from vinyl.lib.table_methods import (
    _adjust_fill_list,
    _build_spine,
    _difference_two,
    _find_ibis_backends,
    _join_spine,
    _process_multiple_select,
    _union_two,
    fill_type,
)
from vinyl.lib.utils.context import _is_notebook
from vinyl.lib.utils.functions import _validate
from vinyl.lib.utils.obj import is_valid_class_name, to_valid_class_name
from vinyl.lib.utils.text import (
    _create_reproducible_hash,
    _generate_random_ascii_string,
)

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    import pyarrow as pa

    from vinyl.lib.chart import geom
    from vinyl.lib.metric import MetricStore

_RULES: list[Callable[..., Any]] = [
    # qualify,
    pushdown_projections,
    normalize,
    unnest_subqueries,
    pushdown_predicates,
    # optimize_joins,  # produces incorrect results
    eliminate_subqueries,
    # merge_subqueries,  # produces incorrect results
    eliminate_joins,
    eliminate_ctes,
    # quote_identifiers,
    # annotate_types,
    # canonicalize,
    # simplify,
]

# more minimal rules for unnesting query before execution and reducing length
_UNNEST_RULES: list[Callable[..., Any]] = [unnest_subqueries, eliminate_subqueries]
_UNNEST_AND_REDUCE_LENGTH_RULES: list[Callable[..., Any]] = [
    unnest_subqueries,
    eliminate_subqueries,
    pushdown_predicates,
]


def _base_ensure_output(func, inst, *args, **kwargs):
    # cache current objects if immutable
    if not inst._mutable:
        cached_arg = inst._arg
        cached_conn_replace = inst._conn_replace
        cached_twin_conn_replace = inst._twin_conn_replace
        cached_col_replace = inst._col_replace

    # build the connection dict and set an updated version to be used in the function
    combined_conn_replace = {}
    combined_twin_conn_replace = {}
    combined_col_replace = {}
    for el in [inst, *args, *list(kwargs.values())]:
        if isinstance(el, VinylTable):
            combined_conn_replace.update(el._conn_replace)
            combined_twin_conn_replace.update(el._twin_conn_replace)
            combined_col_replace.update(el._col_replace)

    result = func(inst, *args, **kwargs)

    if not inst._mutable:
        inst._arg = cached_arg
        inst._conn_replace = cached_conn_replace
        inst._twin_conn_replace = cached_twin_conn_replace
        inst._col_replace = cached_col_replace
    else:
        inst._arg = result._arg
        inst._mutable = True  # chain mutability to subsequent function calls
        inst._conn_replace = combined_conn_replace
        inst._twin_conn_replace = combined_twin_conn_replace
        inst._col_replace = combined_col_replace

    inst._reset_columns()

    final = VinylTable(
        result._arg,
        _conn_replace=combined_conn_replace,
        _twin_conn_replace=combined_twin_conn_replace,
        _col_replace=combined_col_replace,
    )
    final._mutable = inst._mutable
    return final


def _ensure_output(func):
    @wraps(func)
    def wrapper(self: VinylTable, *args, **kwargs) -> VinylTable:
        return _base_ensure_output(func, self, *args, **kwargs)

    return wrapper


class VinylTable:
    _arg: ir.Expr
    _mutable: bool
    _conn_replace: dict[ops.Relation, ops.Relation]
    _twin_conn_replace: dict[ops.Relation, ops.Relation]
    _col_replace: dict[ops.Relation, dict[str, str]]
    _is_vinyl_source: bool
    _source_class: object
    _join_instances_helper: list[VinylTable]

    def __init__(
        self,
        _arg: ir.Expr,
        _conn_replace: dict[ops.Relation, ops.Relation] = {},
        _twin_conn_replace: dict[ops.Relation, ops.Relation] = {},
        _col_replace: dict[ops.Relation, dict[str, str]] = {},
    ):
        self._arg = _arg
        self._mutable = False
        self._conn_replace = _conn_replace
        self._twin_conn_replace = _twin_conn_replace
        self._col_replace = _col_replace
        self._set_columns()

    def _recursive_set_attr(self, name, obj):
        if hasattr(self, name):
            self._recursive_set_attr(f"{name}_", obj)
        else:
            setattr(self, name, obj)

    def _set_columns(self, deferred=False):
        # set columns
        prev_replacements = []
        for i, (name, type_) in enumerate(self.tbl.schema().items()):
            col = VinylColumn(getattr(_, name) if deferred else getattr(self.tbl, name))

            # allow for direct access via x.col instead of only getattr(x, col) if the column name is not a valid class name
            if is_valid_class_name(name):
                self._recursive_set_attr(name, col)

            else:
                new_name = to_valid_class_name(name, prev_replacements)
                prev_replacements.append(new_name)
                self._recursive_set_attr(new_name, col)

            self._recursive_set_attr(f"_{i}", col)

    def _clear_columns(self):
        for name in self.__dict__.copy():
            if name not in [
                "_arg",
                "_mutable",
                "_conn_replace",
                "_twin_conn_replace",
                "_col_replace",
                "_is_vinyl_source",
                "_source_class",
            ]:
                delattr(self, name)

    def _reset_columns(self, deferred=False):
        self._clear_columns()
        self._set_columns(deferred=deferred)

    # Make callable so that @model wrapper works
    def __call__(self) -> VinylTable:
        return self

    # create column function autocomplete
    def __getattr__(self, name) -> VinylColumn:
        return self.__getattribute__(name)

    # allow you to access columns by name like x['col_name']
    def __getitem__(self, key):
        return getattr(self, key)

    def __enter__(self):
        # Create a copy of the original object and make the object mutable
        new = self._copy()
        new._mutable = True
        return new

    def __exit__(self, exc_type, exc_value, traceback):
        # Exit logic here
        pass

    def __str__(self):
        return self.tbl.__str__()

    def __repr__(self):
        return self.tbl.__repr__()

    @property
    def tbl(self):
        return ir.Table(self._arg)

    # @lru_cache(None)
    def _copy(self, mutable: bool | None = None, isolate: bool = True) -> VinylTable:
        new = VinylTable(
            self._arg, self._conn_replace, self._twin_conn_replace, self._col_replace
        )
        if isolate and isinstance(self.tbl.op(), ops.UnboundTable):
            new = new.select(new.columns)  # prevents naming issues

        if mutable is None:
            new._mutable = self._mutable
        else:
            new._mutable = mutable
        return new

    @_ensure_output
    def __add__(self, other) -> VinylTable:
        # Handle adding CustomNumber to 0, which is the default start value for sum
        if not isinstance(other, VinylTable):
            if other == 0:
                return self

            raise ValueError(
                f"Can only add a VinylTable to another VinylTable, not a {type(other)}"
            )

        return _union_two(self.tbl, other.tbl)

    def __radd__(self, other) -> VinylTable:
        if not isinstance(other, VinylTable):
            raise ValueError(
                f"Can only add a VinylTable to another VinylTable, not a {type(other)}"
            )
        return other.__add__(self)

    @_ensure_output
    def __sub__(self, other) -> VinylTable:
        if not isinstance(other, VinylTable):
            raise ValueError(
                f"Can only subtract a VinylTable from another VinylTable, not a {type(other)}"
            )
        return _difference_two(self.tbl, other.tbl)

    def __rsub__(self, other) -> VinylTable:
        if not isinstance(other, VinylTable):
            raise ValueError(
                f"Can only subtract a VinylTable from another VinylTable, not a {type(other)}"
            )
        return other.__sub__(self)

    @_ensure_output
    def __mul__(self, other) -> VinylTable:
        if not isinstance(other, VinylTable):
            raise ValueError(
                f"Can only multiply a VinylTable by another VinylTable, not a {type(other)}"
            )

        return _convert_auto_join_to_ibis_join(
            *_auto_join_helper([self, other], allow_cross_join=True)
        )

    def __rmul__(self, other) -> VinylTable:
        if not isinstance(other, VinylTable):
            raise ValueError(
                f"Can only multiply a VinylTable by another VinylTable, not a {type(other)}"
            )
        return other.__mul__(self)

    @_ensure_output
    def select(
        self,
        cols: column_type,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        window_type: WindowType = WindowType.rows,
        window_bounds: tuple[int | None, int | None] = (None, None),
        fill: fill_type = None,
    ) -> VinylTable:
        """
        Computes a new table with the columns in cols. Can be a single column, a list of columns, or a dictionary of columns with their new names as keys. The column values themselves can be specified as strings (the column name), table attributes, one-argument lambda functions, or selectors.

        If an aggregated column is passed, this will be treated as a windowed column, using the by field for partitioning, the sort field for ordering, and the window_type and window_bounds fields for the actual window.

        Fill can be used optionally to add interpolation to cols. You must either specify one value for each column or a list of values that is the same length as the column list
        """
        # get adjusted col names
        vinyl_by = ColumnListBuilder(self.tbl, by, unique=True)

        # need a copy of sort columns with asc() and desc() applied for sort and one without for selection
        vinyl_sort = SortColumnListBuilder(self.tbl, sort, unique=True, reverse=False)

        vinyl_by_and_sort = ColumnListBuilder(
            self.tbl, vinyl_by._queryable + vinyl_sort._unsorted, unique=True
        )

        vinyl_cols = ColumnListBuilder(self.tbl, cols, unique=True)

        if (
            len(vinyl_by._queryable) == 0
            and len(vinyl_sort._unsorted) == 0
            and fill is None
        ):
            out = self.tbl.select(*vinyl_cols._queryable)
            return out

        window_ = ibis.window(
            group_by=None if by is None else vinyl_by._queryable,
            order_by=None if sort is None else vinyl_sort._sorted,
            range=(window_bounds if window_type == WindowType.range else None),
            rows=(window_bounds if window_type == WindowType.rows else None),
        )

        source_cols_to_select = ColumnListBuilder(
            self.tbl, vinyl_by_and_sort._queryable + vinyl_cols._sources_as_deferred
        )

        # Adjust for window
        windowed = vinyl_cols._windowize(window_)
        adj_cols_to_select = vinyl_by_and_sort + windowed

        # make simple selection if no fill or by
        adj_window_ = ibis.window(
            group_by=None if by is None else vinyl_by._names_as_deferred,
            order_by=None if sort is None else vinyl_sort._names_as_deferred_sorted,
            range=(window_bounds if window_type == WindowType.range else None),
            rows=(window_bounds if window_type == WindowType.rows else None),
        )

        if fill is None or len(vinyl_by_and_sort._cols) == 0:
            out = self.tbl.select(adj_cols_to_select._queryable)
            if vinyl_sort._sorted != []:
                out = out.order_by(vinyl_sort._names_as_deferred_resolved_sorted(out))

            return out

        # build spine
        spine, rename_dict = _build_spine(self.tbl, vinyl_by_and_sort._queryable)
        fill_list = _adjust_fill_list(len(vinyl_cols._cols), fill)

        # union spine and preaggregated table
        unioned = _join_spine(self.tbl.select(source_cols_to_select._queryable), spine)
        unioned_cols = ColumnListBuilder(unioned, vinyl_cols._lambdaized, unique=True)
        unioned_cols._windowize(adj_window_, adj_object=True)

        # perform base window calculations
        new_adj_cols_to_select = ColumnListBuilder(
            unioned,
            vinyl_by._names_as_deferred
            + vinyl_sort._names_as_deferred
            + unioned_cols._queryable,
            unique=True,
        )  # recreate windows with original cols

        filled = unioned.select(*new_adj_cols_to_select._queryable).rename(rename_dict)

        if all([i == FillOptions.null for i in fill_list]):
            if vinyl_sort._cols == []:
                return filled
            return filled.order_by(vinyl_sort._names_as_deferred_sorted)

        for i, col in enumerate(vinyl_cols):
            # switch to VinylTable to access deferred method
            filled = VinylTable(
                filled._arg,
                self._conn_replace,
                self._twin_conn_replace,
                self._col_replace,
            )
            filled._mutable = self._mutable
            filled = filled._interpolate(
                col._name_as_deferred_resolved(filled.tbl),
                sort=vinyl_sort._names_as_deferred_resolved_sorted(filled.tbl),
                by=vinyl_by._names_as_deferred_resolved(filled.tbl),
                fill=fill_list[i],
            )
        final_sort_cols = vinyl_sort._names_as_deferred_resolved_sorted(
            filled.tbl
        ) + vinyl_by._names_as_deferred_resolved(filled.tbl)
        if final_sort_cols == []:
            return filled
        return filled.sort(final_sort_cols)

    @_ensure_output
    def select_all(
        self,
        col_selector: column_type_all,
        f: Callable[[Any], Any] | list[Callable[[Any], Any] | None] | None,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        window_type: WindowType = WindowType.rows,
        window_bounds: tuple[int | None, int | None] = (None, None),
        fill: fill_type = None,
        rename: bool = False,
    ) -> VinylTable:
        """
        Select_all is a generalized form of `select` that can apply apply the same operation (specified in _f_) to multiple columns. The col_selector field can be a list of column fields, where each element  `select`, and _f_ should be a list of functions of the same length.

        If _f_ is a single function, it will be applied to all columns. If _f_ is a list of functions, the functions will be applied to the corresponding columns. If _f_ is shorter than the number of columns, the last function will be applied to all remaining columns.

        By, sort, window_type, and window_bounds operate as in `select`.

        If rename is True, the columns will be renamed to the name of the function that was applied to them. If rename is False, the columns will names to the original column name.
        """
        adj_cols = _process_multiple_select(self.tbl, col_selector, f, rename=rename)
        return self.select(adj_cols, by, sort, window_type, window_bounds, fill)

    @_ensure_output
    def define(
        self,
        cols: column_type,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        window_type: WindowType = WindowType.rows,
        window_bounds: tuple[int | None, int | None] = (None, None),
        fill: fill_type = None,
    ) -> VinylTable:
        """
        Mutate is identical to `select`, except all current columns are included, and the new columns are added to the table. If a new column has the same name as an existing column, the existing column will be replaced.
        """
        vinyl_cols = ColumnListBuilder(self.tbl, cols)
        vinyl_by = ColumnListBuilder(self.tbl, by)
        vinyl_sort = SortColumnListBuilder(self.tbl, sort, reverse=False)

        out = self.select_all(
            col_selector=[s.all()] + vinyl_cols._queryable,
            f=[lambda x: x] + [None] * len(vinyl_cols._queryable),
            by=vinyl_by._queryable,
            sort=vinyl_sort._sorted,
            window_type=window_type,
            window_bounds=window_bounds,
            rename=True,
        )
        return out

    @_ensure_output
    def define_all(
        self,
        col_selector: column_type_all,
        f: Callable[..., Any] | list[Callable[..., Any] | None] | None,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        window_type: WindowType = WindowType.rows,
        window_bounds: tuple[int | None, int | None] = (None, None),
        fill: fill_type = None,
        rename: bool = False,
    ) -> VinylTable:
        """
        Mutate_all is identical to `select_all`, except all current columns are included, and the new columns are added to the table. If a new column has the same name as an existing column, the existing column will be replaced.
        """
        col_selector_list = (
            [col_selector] if not isinstance(col_selector, list) else col_selector
        )
        f_list = [f] if not isinstance(f, list) else f
        if len(f_list) == 1 and len(col_selector_list) > 1:
            f_list = f_list * len(col_selector_list)

        return self.select_all(
            col_selector=[s.all()]
            + col_selector_list,  # ibis handles renames automtically
            f=[lambda x: x, *f_list],
            by=by,
            sort=sort,
            window_type=window_type,
            window_bounds=window_bounds,
            rename=rename,
        )

    @_ensure_output
    def aggregate(
        self,
        cols: column_type,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        fill: fill_type = None,
    ) -> VinylTable:
        """
        Returns an aggregated table for cols, grouped by `by` and `sort`.

        If fill is specified, the table will be interpolated using the specified fill strategy, taking into account direction from the `sort` argument. `fill` can either be a single value or a list of values, one for each column in `cols`.
        """
        vinyl_cols = ColumnListBuilder(self.tbl, cols)
        vinyl_by = ColumnListBuilder(self.tbl, by)
        vinyl_sort = SortColumnListBuilder(self.tbl, sort, reverse=False)
        spine_cols = ColumnListBuilder(
            self.tbl, vinyl_by._queryable + vinyl_sort._unsorted, unique=True
        )
        unadj_tbl = self.tbl.aggregate(
            metrics=vinyl_cols._queryable, by=spine_cols._queryable, having=()
        )

        if fill is None or len(spine_cols._cols) == 0:
            sort_cols = vinyl_sort._names_as_deferred_resolved_sorted(unadj_tbl)
            # Don't support having argument. use filter instead
            if sort_cols == []:
                return unadj_tbl
            else:
                return unadj_tbl.order_by(sort_cols)

        spine, rename_dict = _build_spine(self.tbl, spine_cols._queryable)
        if spine is None:
            return unadj_tbl

        adj_aggregate = unadj_tbl.rename(rename_dict)
        null_fill = _join_spine(
            adj_aggregate, spine
        )  # rejoin spine to ensure all by times/dates are present

        filled = null_fill
        fill_list = _adjust_fill_list(len(vinyl_cols._cols), fill)
        if all([i == FillOptions.null for i in fill_list]):
            if vinyl_sort._cols == []:
                return filled
            return filled.order_by(vinyl_sort._names_as_deferred_sorted)
        # handle factor

        for i, col in enumerate(vinyl_cols):
            # switch to VinylTable to access deferred method
            filled = VinylTable(
                filled._arg,
                self._conn_replace,
                self._twin_conn_replace,
                self._col_replace,
            )
            filled._mutable = self._mutable
            filled = filled._interpolate(
                col._name_as_deferred_resolved(filled.tbl),
                sort=vinyl_sort._names_as_deferred_resolved_sorted(filled.tbl),
                by=vinyl_by._names_as_deferred_resolved(filled.tbl),
                fill=fill_list[i],
            )
        final_sort_cols = vinyl_sort._names_as_deferred_resolved_sorted(
            filled.tbl
        ) + vinyl_by._names_as_deferred_resolved(filled.tbl)
        if final_sort_cols == []:
            return filled
        return filled.sort(final_sort_cols)

    def _colname_helper(self):
        final_tbl_op = self.tbl.op()
        new_conn_replace = {k: v for k, v in self._conn_replace.items()}
        new_twin_conn_replace = {k: v for k, v in self._twin_conn_replace.items()}
        for tbl, col_replace in self._col_replace.items():
            new_schema_pairs = []
            for name, type_ in tbl.schema.items():
                if name in col_replace:
                    new_schema_pairs.append((col_replace[name], type_))
                else:
                    new_schema_pairs.append((name, type_))

            new_tbl = ops.UnboundTable(
                tbl.name, ibis.schema(new_schema_pairs), namespace=tbl.namespace
            )
            full_replace = {tbl: new_tbl}
            for old, new in col_replace.items():
                full_replace[ops.Field(tbl, old)] = ops.Field(new_tbl, new)

            # handle join chain replacements

            final_tbl_op = final_tbl_op.replace(full_replace)

            if tbl in new_conn_replace:
                new_conn_replace[new_tbl] = new_conn_replace.pop(tbl)

            if tbl in new_twin_conn_replace:
                new_twin_conn_replace[new_tbl] = new_twin_conn_replace.pop(tbl)

        out = VinylTable(
            _arg=final_tbl_op,
            _conn_replace=new_conn_replace,
            _twin_conn_replace=new_twin_conn_replace,
            _col_replace={},
        )
        if self._mutable:
            out._mutable = True
            self = out

        return out

    def _execution_replace(
        self: VinylTable, twin: bool = False, limit: int | None = None
    ):
        self = self._colname_helper()

        unactivated_conn_replace = (
            self._twin_conn_replace if twin else self._conn_replace
        )

        if unactivated_conn_replace == {}:
            if self.tbl._find_backends()[0] != [] or isinstance(
                self.tbl.op(), ops.InMemoryTable
            ):
                # not an unbound table, so was created outside the context of a project. can just return as is
                return self.tbl

            elif twin is True:
                ValueError(
                    "No twin connection found. Please ensure your twin connection is correctly set up."
                )

            else:
                raise ValueError(
                    "No connection found. Please ensure your connection is correctly set up."
                )

        # activate conn replace by calling the function
        active_conn_replace = {}
        for k, v in unactivated_conn_replace.items():
            activated = v()
            active_conn_replace[k] = activated

        replaced = self.tbl.op().replace(active_conn_replace).to_expr()
        replaced = replaced.limit(limit) if limit is not None else replaced

        return replaced

    def _execution_helper(
        self: VinylTable, twin=False, limit: int | None = 10000
    ) -> ir.Table:
        # replace connections
        replaced = self._execution_replace(twin, limit)

        # handle queries with multiple backends
        if len(_find_ibis_backends(replaced)) > 1:
            return _unify_backends(replaced)
        return replaced

    def visualize(self):
        """
        Print a visualize representation of the query plan
        """
        return VinylGraph._visualize(self.tbl)

    def execute(
        self,
        format: Literal["pandas", "polars", "pyarrow", "torch", "text"] = "pandas",
        means: Literal[
            "direct", "full_sql", "unnested", "unnested_and_pushed_down", "optimized"
        ] = "direct",
        twin: bool = False,
        limit: int | None = 10000,
    ) -> Any:
        """
        Run the query and return the result in the specified format. If twin is True, the twin connection will be used.

        To execute via the sql instead of the ibis backend, use means=sql or means=optimized_sql. Note that in this case, a pandas result will be returned no matter what. In particular, the main reason to use the `optimized_sql` means is in situations where the ibis compiled sql is too long or nested to be processed by the backend.
        """
        replaced = self._execution_helper(twin, limit)
        if means != "direct":
            backend = replaced._find_backend()
            backend._run_pre_execute_hooks(self.tbl)
            table = replaced.as_table()
            sql = backend.compile(table, limit=limit)
            if means != "sql":
                if means == "unnested":
                    rules = _UNNEST_RULES
                elif means == "unnested_and_pushed_down":
                    rules = _UNNEST_AND_REDUCE_LENGTH_RULES
                elif means == "optimized":
                    rules = _RULES
                else:
                    raise ValueError(
                        "means must be one of 'unnested', 'unnested_and_pushed_down', or 'optimized'"
                    )
                sqlglot_dialect = getattr(backend, "_sqlglot_dialect", backend.name)
                sql = optimize(sql, dialect=sqlglot_dialect, rules=rules).sql(
                    dialect=sqlglot_dialect
                )
            schema = table.schema()
            # TODO(kszucs): these methods should be abstractmethods or this default
            # implementation should be removed
            with backend._safe_raw_sql(sql) as cur:
                result = backend._fetch_from_cursor(cur, schema)
            return self.tbl.__pandas_result__(result)
        elif format == "pandas":
            return (
                replaced.to_pyarrow().to_pandas()
            )  # normal ibis execute produces type errors which this resolves
        elif format == "text":
            orig_max_depth = ibis.options.repr.interactive.max_depth
            if _is_notebook():
                ibis.options.repr.interactive.max_depth = 1000
            try:
                return to_rich(replaced)
            finally:
                ibis.options.repr.interactive.max_length = orig_max_depth
        elif format == "pyarrow":
            return replaced.to_pyarrow()
        elif format == "polars":
            try:
                import polars as pl
            except ImportError:
                raise ImportError(
                    "Polars not installed. Please install polars to use it."
                )
            return pl.from_arrow(replaced.to_pyarrow())
        elif format == "torch":
            return replaced.to_torch()
        else:
            raise ValueError(f"Output type {format} not supported")

    def save(
        self,
        path: str | Path,
        format: Literal["csv", "delta", "json", "parquet"] = "csv",
        twin: bool = False,
        limit=10000,
    ):
        """
        Run the query and save the result to the specified path in the specified format.
        """
        replaced = self._execution_helper(twin, limit)

        if format == "csv":
            replaced.to_csv(path)
        elif format == "delta":
            replaced.to_delta(path)
        elif format == "json":
            with open(path, "w") as f:
                f.write(replaced.execute().to_json(orient="records"))
        elif format == "parquet":
            replaced.to_parquet(path)
        else:
            raise ValueError(f"Output type {format} not supported")

    def _pickle(self, path: str | Path, tbl_only=True):
        if tbl_only:
            pkl.dump(self.tbl, open(path, "wb"))
        else:
            pkl.dump(self, open(path, "wb"))
        return

    @_ensure_output
    def aggregate_all(
        self,
        col_selector: column_type_all,
        f: Callable[[Any], Any] | list[Callable[[Any], Any] | None] | None,
        by: column_type | None = None,
        sort: column_type | None = None,  # add support for selectors later
        fill: fill_type = None,
        rename: bool = False,
    ) -> VinylTable:
        """
        Aggregate_all is a generalized form of `aggregate` that can apply apply the same operation (specified in _f_) to multiple columns. The col_selector field can be a list of column fields, where each element  `select`, and _f_ should be a list of functions of the same length.

        If _f_ is a single function, it will be applied to all columns. If _f_ is a list of functions, the functions will be applied to the corresponding columns. If _f_ is shorter than the number of columns, the last function will be applied to all remaining columns.

        By, sort, and fill operate as in `aggregate`.

        If rename is True, the columns will be renamed to the name of the function that was applied to them. If rename is False, the columns will names to the original column name.
        """
        adj_cols = _process_multiple_select(self.tbl, col_selector, f, rename=rename)
        return self.aggregate(cols=adj_cols, by=by, sort=sort, fill=fill)

    @_ensure_output
    def rename(self, rename_dict: dict[str, str]) -> VinylTable:
        """
        Rename columns in the table. The rename_dict should be a dictionary with the new column name as the key and the original column name as the value.
        """
        return self.tbl.rename(rename_dict)

    @_ensure_output
    def relocate(
        self,
        cols: column_type_without_dict,
        before: base_column_type | s.Selector | None = None,
        after: base_column_type | s.Selector | None = None,
    ) -> VinylTable:
        """
        Relocate columns before or after other specified columns.
        """
        vinyl_cols = ColumnListBuilder(self.tbl, cols)
        vinyl_before = (
            ColumnListBuilder(self.tbl, before) if before is not None else None
        )
        vinyl_after = ColumnListBuilder(self.tbl, after) if after is not None else None
        before_names = vinyl_before._names if vinyl_before is not None else []
        after_names = vinyl_after._names if vinyl_after is not None else []

        helper = []
        for ls in [before_names, after_names]:
            if len(ls) > 1:
                helper.append(~s.c(*ls))
            elif len(ls) == 1:
                helper.append(ls[0])
            else:
                helper.append(None)

        return self.tbl.relocate(*vinyl_cols._names, before=helper[0], after=helper[1])

    @_ensure_output
    def _interpolate(
        self,  # should already have had null fill applied
        cols: column_type | None = None,
        sort: column_type | None = None,
        by: column_type | None = None,
        fill: fill_type = FillOptions.null,  # can specify one of the fill options or a lambda function
    ) -> VinylTable:
        vinyl_cols = ColumnListBuilder(self.tbl, cols)
        vinyl_by = ColumnListBuilder(self.tbl, by)
        vinyl_sort = SortColumnListBuilder(
            self.tbl, sort, reverse=True if fill == FillOptions.previous else False
        )
        out: VinylTable = self
        adj_fill = _adjust_fill_list(len(vinyl_cols._cols), fill)
        for i, vinyl_col in enumerate(vinyl_cols._cols):
            fill = adj_fill[i]
            if fill is None:
                continue
            elif fill == FillOptions.null:
                out = out.sort(vinyl_sort._sorted)
                # no need to fill further, should already have n
                continue
            elif callable(fill):
                # initial mutate to allow fill to operate on unaltered columns
                fill_col_name = f"fill_{vinyl_col._name}"
                filled_col = fill(vinyl_col._name_as_deferred_resolved(self.tbl))
                if not isinstance(filled_col, ir.Expr):
                    filled_col = ibis.literal(filled_col)

                out = out.define(
                    {fill_col_name: filled_col},
                    by=vinyl_by._names_as_deferred_resolved(out.tbl),
                    sort=vinyl_sort._names_as_deferred_resolved_sorted(out.tbl),
                )

                fill_col = ColumnBuilder(out.tbl, fill_col_name)
                out = out.define_all(
                    vinyl_col._name_as_deferred_resolved(out.tbl),
                    f=lambda x: x.fillna(fill_col._name_as_deferred_resolved(out.tbl)),
                    by=vinyl_by._names_as_deferred_resolved(out.tbl),
                    sort=vinyl_sort._names_as_deferred_resolved_sorted(out.tbl),
                )
                out = out.drop(fill_col._name_as_deferred_resolved(out.tbl))
            else:
                if sort is None:
                    raise ValueError(
                        "Must provide a sort column when using next or previous fill"
                    )
                sort_helper_col_string = f"helper_{vinyl_col._name}"
                sort_helper_col_base = vinyl_col._name_as_deferred_resolved(out.tbl)
                out = self.define(
                    {
                        sort_helper_col_string: (
                            sort_helper_col_base.count()
                            if sort_helper_col_base is not None
                            else None
                        )
                    },
                    by=vinyl_by._names_as_deferred_resolved(out.tbl),
                    sort=vinyl_sort._names_as_deferred_resolved_sorted(out.tbl),
                    fill=None,
                    window_type=WindowType.rows,
                    window_bounds=(None, 0),
                )
                sort_helper_col = ColumnBuilder(out.tbl, sort_helper_col_string)
                helper_col = vinyl_col._name_as_deferred_resolved(out.tbl)
                out = out.define(
                    {
                        vinyl_col._name: (
                            helper_col.max() if helper_col is not None else None
                        )
                    },
                    by=vinyl_by._names_as_deferred_resolved(out.tbl)
                    + [sort_helper_col._name_as_deferred_resolved(out.tbl)],
                )
                out = out.drop(sort_helper_col._name_as_deferred_resolved(out.tbl))
                out = out.sort(vinyl_sort._names_as_deferred_resolved_sorted(out.tbl))

        return out

    # need to demote args because chart is not included in validation
    @_demote_args
    def chart(
        self,
        geoms: (
            geom | list[Any]
        ),  # always will be a geom, but listing any here to avoid import of lets-plot unless necessary
        x: ir.Value | None,
        y: ir.Value | None = None,
        color: ir.Value | None = None,
        fill: ir.Value | None = None,
        size: ir.Value | None = None,
        alpha: ir.Value | None = None,
        facet: ir.Value | list[ir.Value] | None = None,
        coord_flip: bool = False,
        interactive: bool = True,
    ):
        """
        Visualize the table using a chart. The geoms argument should be a geom or a list of geoms. The x, y, color, fill, size, alpha, and facet arguments should be column expressions. If a list of columns is passed, the chart will be faceted by the columns in the list.

        If coord_flip is True, the x and y axes will be flipped.
        """
        from lets_plot import LetsPlot

        from vinyl.lib.chart import BaseChart

        if interactive:
            LetsPlot.setup_html()
        else:
            LetsPlot.setup_html(no_js=True)

        return BaseChart(
            geoms, self, x, y, color, fill, size, alpha, facet, coord_flip
        )._show()

    def _to_sql_ast(
        self,
        dialect=None,
        optimized=False,
        relative_to: dict[str, Any] = {},
        node_name=None,
        name_required=False,
    ):
        """
        Output the table as a SQL string. The dialect argument can be used to specify the SQL dialect to use.

        If optimized is True, the SQL will be optimized using the SQLglot optimizer. If formatted is True, the SQL will be formatted for readability.

        Relative_to should be a dictionary of named objects, where the objects can be either VinylTables or MetricStores.
        """
        if node_name is None:
            try:
                node_name = self.get_adj_node_name(self)
            except ValueError:
                if name_required:
                    raise ValueError(
                        "Node name required for SQL output. Please provide a node name."
                    )
                node_name = _generate_random_ascii_string(10)

        # self = self._colname_helper()
        expr = self._execution_replace(limit=None)
        if dialect is None:
            try:
                backend = _find_ibis_backends(expr)[0]
            except com.IbisError:
                # default to duckdb for SQL compilation because it supports the
                # widest array of ibis features for SQL backends
                backend = ibis.duckdb
                dialect = ibis.options.sql.default_dialect
            else:
                dialect = backend.dialect
        else:
            try:
                backend = getattr(ibis, dialect)
            except AttributeError:
                raise ValueError(f"Unknown dialect {dialect}")
            else:
                dialect = getattr(backend, "dialect", dialect)
        if relative_to != {}:
            replace_dict = {}
            for name, obj in relative_to.items():
                if isinstance(obj, VinylTable):
                    vinyltbl = obj
                else:
                    from vinyl.lib.metric import MetricStore

                    if isinstance(obj, MetricStore) and obj._default_tbl is not None:
                        vinyltbl = obj._default_tbl
                    else:
                        raise ValueError(
                            "relative_to should be a VinylTable or a MetricStore"
                        )

                tbl_op = vinyltbl._execution_replace().op()
                new_tbl = ops.UnboundTable(
                    name,
                    ibis.schema(
                        [(name, type_) for name, type_ in tbl_op.schema.items()]
                    ),
                )
                replace_dict[tbl_op] = new_tbl
            expr = expr.op().replace(replace_dict).to_expr()

        # fix a BQ-specific Ibis bug that occurs with caching
        if not hasattr(backend, "_session_dataset") and isinstance(
            backend, ibis.backends.bigquery.Backend
        ):
            backend._session_dataset = None

        sg_expr = backend._to_sqlglot(expr.unbind())
        sg_tbl = exp.Table(this=exp.Identifier(this=node_name))
        if optimized:
            dont_optimize = False
            # check if table is qualified
            try:
                validate_qualify_columns(sg_expr)
                schema = None
            except Exception:
                # if not qualified, qualify
                schema = {}
                for root in expr.op().find(ops.DatabaseTable):
                    schema_name = exp.Table(
                        this=exp.Identifier(this=root.args[0], quoted=True),
                        catalog=exp.Identifier(this=root.args[-1].catalog, quoted=True),
                        db=exp.Identifier(this=root.args[-1].database, quoted=True),
                    )
                    schema[schema_name] = {k: str(v) for k, v in root.args[1].items()}
                try:
                    sg_expr = qualify(sg_expr, schema=schema, dialect=dialect)
                    validate_qualify_columns(sg_expr)
                except Exception:
                    # if qualify fails, don't optimize, won't work
                    dont_optimize = True
            if not dont_optimize:
                sg_expr = optimize(
                    sg_expr, schema=schema, dialect=dialect, rules=_RULES
                )

        return (
            sg_expr,
            {sg_tbl: expr.schema()},
            dialect,
        )

    ## modified version of ibis.sql that modifies sqlglot behavior to (1) minimize parsing and (2) optimize if requested
    def to_sql(
        self,
        dialect=None,
        optimized=False,
        formatted=True,
        relative_to: dict[str, VinylTable] = {},
        node_name: str | None = None,
    ) -> str:
        """
        Output the table as a SQL string. The dialect argument can be used to specify the SQL dialect to use.

        If optimized is True, the SQL will be optimized using the SQLglot optimizer. If formatted is True, the SQL will be formatted for readability.
        """
        sg_expr, _, _ = self._to_sql_ast(
            dialect, optimized, relative_to, node_name, name_required=False
        )
        sql = sg_expr.sql(dialect=dialect, pretty=formatted)

        return sql

    @_ensure_output
    def distinct(
        self,
        on: column_type_without_dict | None = None,
        keep: Literal["first", "last"] | None = "first",
    ) -> VinylTable:
        """
        Return distinct rows from the table.

        If `on` is specified, the distinct rows will be based on the columns in `on`. If it is not, the distinct rows will be based on all columns.

        If `keep` is specified, the first or last row will be kept.
        """
        if on is not None:
            on = ColumnListBuilder(self.tbl, on, unique=True)._names
        return self.tbl.distinct(on=on, keep=keep)

    @_ensure_output
    def drop(self, cols: column_type_without_dict) -> VinylTable:
        """
        Remove columns from the table.
        """
        vinyl_cols = ColumnListBuilder(self.tbl, cols)
        return self.select(~s._to_selector(vinyl_cols._names))

    @_ensure_output
    def dropna(
        self,
        on: column_type_without_dict | None = None,
        how: Literal["any", "all"] = "any",
    ) -> VinylTable:
        """
        Remove rows from the table with missing values.

        If `on` is specified, the missing values will be checked for the columns in `on`. If it is not, the missing values will be checked for all columns.

        If `how` is 'any', the row will be removed if any of the values are missing. If it is 'all', the row will be removed if all of the values are missing.
        """
        if on is not None:
            on = ColumnListBuilder(self.tbl, on, unique=True)._names
        return self.tbl.dropna(subset=on, how=how)

    @_ensure_output
    def sort(
        self,
        by: column_type | None = None,
    ) -> VinylTable:
        """
        Sort the table by the columns in `by`.

        If `by` is not specified, the table will be sorted by all columns.

        To sort a column in descending order, place a `-` in front of the column.
        """
        if by is None:
            return self.tbl
        return self.tbl.order_by(by)

    @_ensure_output
    def limit(self, n: int | None, offset: int = 0) -> VinylTable:
        """
        Return the first `n` rows of the table, starting at the `offset` row.

        Note that the result set may not be idempotent.
        """
        return self.tbl.limit(n, offset)

    @_ensure_output
    def filter(self, conditions: boolean_column_type) -> VinylTable:
        """
        Filter the table based on the conditions specified. This function should be used in place of WHERE, HAVING, and QUALIFY clauses in SQL.
        """
        if isinstance(conditions, list):
            return self.tbl.filter(*conditions)
        return self.tbl.filter(conditions)

    def filter_all(
        self,
        col_selector: column_type_all,
        condition_f: Callable[..., Any] | list[Callable[..., Any] | None] | None,
        condition_type: Literal["and", "or"] = "and",
    ) -> VinylTable:
        """
        Similar to other '_all' method variants, this is a generalized form of `filter` that can apply the same operation (specified in _condition_f_) to multiple columns.

        The col_selector field can be a list of column fields, where each element  `select`, and _condition_f_ should be a list of functions of the same length.

        Useful if you want to apply the same filter (e.g. value > 0) to multiple columns.

        Conditions are evaluated together using the condition_type argument. If condition_type is 'and', all conditions must be met. If condition_type is 'or', any condition can be met. If you'd like to use a mix of 'and' and 'or' conditions, call the `filter` function multiple times.
        """
        adj_cols = _process_multiple_select(
            self.tbl, col_selector, condition_f, rename=False
        )
        if condition_type == "and":
            return self.filter(adj_cols)
        else:
            for i, col in enumerate(adj_cols):
                if i == 0:
                    combined_cond = col
                else:
                    combined_cond |= col
            return self.filter(combined_cond)

    def _count_base(
        self,
        where: base_boolean_column_type | None = None,
        distinct: bool = False,
    ) -> ir.Value:
        vinyl_where = ColumnBuilder(self.tbl, where)

        base = (
            self.tbl.nunique(where=vinyl_where._col)
            if distinct
            else self.tbl.count(where=vinyl_where._col)
        )

        return base

    def _count_scalar(
        self,
        where: base_boolean_column_type | None = None,
        distinct: bool = False,
    ) -> ir.Value:
        return self._copy()._count_base(where, distinct)

    @_ensure_output
    def _count_table(
        self,
        where: base_boolean_column_type | None = None,
        distinct: bool = False,
    ) -> VinylTable:
        return self._count_base(where, distinct).as_table()

    def count(
        self,
        where: base_boolean_column_type | None = None,
        distinct: bool = False,
        as_scalar=False,
    ) -> VinylTable | ir.Value:
        """
        Return the count of rows in the table.

        If `where` is specified, the count will be based on the rows that meet the condition. If it is not, the count will be based on all rows.

        If `distinct` is True, the count will be based on distinct rows.

        If `as_scalar` is True, the result will be returned as a scalar. If it is False, the result will be returned as a table. By default, a table is returned.
        """
        if as_scalar:
            return self._count_scalar(where, distinct)
        return self._count_table(where, distinct)

    @_ensure_output
    def pivot(
        self,
        colnames_from: str | list[str],
        values_from: str | list[str],
        values_fill: Callable[..., Any] | None = None,
        values_agg: Callable[[ir.Value], ir.Scalar] = lambda x: x.first(),
        colnames_sep: str = "_",
        colnames_sort: bool = False,
        colnames_prefix: str = "",
        id_cols: str | list[str] | None = None,
    ):
        """
        Pivot a table to a wider format.

        <u>Argument descriptions</u>
        *colnames_from*: The columns to use as the names of the new columns
        *colnames_sep*: The separator to use when combining the colnames_from columns, if more than one is specified
        *colnames_prefix*: The prefix to use for the new columns
        *colnames_sort*: Whether to sort the names of the new columns. If False, the names will be sorted in the order they are found in the table.
        *values_from*: The columns to use as the values of the new columns
        *values_fill*: The fill value to use for missing values in the new columns. Defaults to null
        *values_agg*: The aggregation function to use for the new columns. Defaults to the first value.
        *id_cols*: The columns that uniquely specify each row. If None, all columns not specified in colnames_from or values_from will be used.

        """
        return self.tbl.pivot_wider(
            id_cols=id_cols,
            names_from=colnames_from,
            values_from=values_from,
            values_fill=values_fill,
            values_agg=values_agg,
            names_sep=colnames_sep,
            names_sort=colnames_sort,
            names_prefix=colnames_prefix,
        )

    @_ensure_output
    def unpivot(
        self,
        cols: str | list[str],
        colnames_to: str = "name",
        colnames_transform: Callable[..., ir.Value] | None = None,
        values_to: str = "value",
        values_transform: Callable[..., ir.Value] | None = None,
    ) -> VinylTable:
        """
        Transform a table from wider to longer.

        <u>Argument descriptions</u>
        *cols*: The column names to unpivot
        *colnames_to*: The name of the new column to store the names of the original columns
        *colnames_transform*: A function to transform the names of the original columns to be stored in the `names_to` column
        *values_to*: The name of the new column to store the values of the original columns
        *values_transform*: A function to transform the values of the original columns to be stored in the `values_to` column

        """
        adj_col_names = ColumnListBuilder(self.tbl, cols, unique=True)._names
        return self.tbl.pivot_longer(
            s.c(*adj_col_names),
            names_to=colnames_to,
            names_transform=colnames_transform,
            values_to=values_to,
            values_transform=values_transform,
        )

    def schema(self) -> VinylSchema:
        """
        Return the schema of the table.
        """
        ibis_schema = VinylSchema(self.tbl.schema())
        return ibis_schema

    def get_name(self) -> str:
        """
        Return the name of the table.
        """
        return self.tbl.get_name()

    def _decompile(self) -> str:
        return ibis.decompile(self.tbl)

    def _reproducible_hash(self) -> str:
        return _create_reproducible_hash(self._decompile())

    @property
    def columns(self) -> list[str]:
        """
        Return the column names of the table.
        """
        return self.tbl.columns

    @_ensure_output
    def sample(self, fraction: float, method: Literal["row", "block"]) -> VinylTable:
        """
        Sample a fraction of rows from a table. Results may not be idempotent.

        See specific note from Ibis below:

        Sampling is by definition a random operation. Some backends support specifying a seed for repeatable results, but not all backends support that option. And some backends (duckdb, for example) do support specifying a seed but may still not have repeatable results in all cases.
        In all cases, results are backend-specific. An execution against one backend is unlikely to sample the same rows when executed against a different backend, even with the same seed set.
        """
        return self.tbl.sample(fraction, method)

    def _get_documentation(self, class_name=False):
        """
        Returns a table with the available documentation for the table, using column-level lineage to pull field description and pk/fk information from upstread sources.

        If `class_name`is false, fk and pk information is returned with the table name, otherwise it is returned with the (shorter) class name.

        """
        unaltered_cols = VinylGraph._find_unaltered_cols(self)
        unaltered_hash_dict = {hash(v): k for k, v in unaltered_cols.items()}
        colnames = self.columns
        cols = [getattr(self, colname) for colname in colnames]
        out = []
        for i, col in enumerate(cols):
            out_it = {}
            out_it["pos"] = i
            out_it["name"] = colnames[i]
            hash_col = hash(col._col.op())
            if hash_col in unaltered_hash_dict:
                name, field = Field.get(unaltered_hash_dict[hash_col])
                out_it["direct_source"] = (
                    f'{name.split(".")[-1]}.{field.name}'
                    if class_name
                    else f"{name}, {field.name}"
                )
                out_it["description"] = (
                    field.description if hasattr(field, "description") else None
                )
                out_it["primary_key"] = (
                    field.primary_key if hasattr(field, "primary_key") else False
                )
                if hasattr(field, "unique"):
                    unique = field.unique
                    if unique is None:
                        pass
                    elif unique is True:
                        out_it["is_unique"] = True
                    else:
                        out_it["is_unique"] = False

                if hasattr(field, "foreign_key"):
                    fk = field.foreign_key
                    if fk is not None:
                        name, field = Field.get(fk)
                        out_it["foreign_key"] = (
                            f'{name.split(".")[-1]}.{field.name}'
                            if class_name
                            else f"{name}, {field.name}"
                        )

            out.append(out_it)

        return self.from_memory(out)

    def get_backend(self):
        return self.tbl._find_backend()

    def eda(
        self,
        cols: column_type | None = None,
        topk: int = 3,
        calculate_distinct_values: bool = True,
        descriptive_stats: bool = True,
        with_docs=False,
        docs_class_name=False,
    ) -> VinylTable:
        """
        Return summary statistics for each column in the table.

        If cols is specified, the summary statistics will be returned for the columns in cols. If it is not, the summary statistics will be returned for all columns.
        """
        if cols is None:
            cols = self.columns
        vinyl_cols = ColumnListBuilder(self.tbl, cols, unique=True)
        to_include = vinyl_cols._names
        aggs = []
        backend = self._execution_helper()._find_backend()

        for pos, colname in enumerate(self.columns):
            if colname not in to_include:
                continue
            tbl = self.tbl.select(colname)
            col = tbl[colname]
            none_col = ibis.literal(None).cast(str)
            type_col = type(col)
            typ = col.type()
            if isinstance(typ, dt.JSON):
                if isinstance(self.get_backend(), BigqueryBackend):
                    # bigquery doesn't support casting to json, so we need to convert to string first
                    tbl = ops.SQLStringView(
                        child=tbl.alias("t").op(),
                        query=f"select to_json_string(`{colname}`) as `{colname}` from t",
                        schema=ibis.schema([(colname, dt.String)]),
                    ).to_expr()
                else:
                    tbl = tbl.mutate(**{colname: col.cast(dt.String)})

                col = tbl[colname]
            agg = tbl.mutate(
                isna=ibis.case().when(col.isnull(), 1).else_(0).end(),
            )
            column_dict = {
                "pos": lit(pos),
                "name": lit(colname),
                "type": lit(str(typ)),
                "nullable": lit(typ.nullable),
                "nulls": _.isna.sum(),
                "non_nulls": (1 - _.isna).sum(),
                "null_frac": _.isna.mean().round(3),
                "n_distinct": col.nunique(),
            }
            rename_dict = {"position": "pos"}

            if calculate_distinct_values:
                distinct_col = _[colname].nunique()
                count_col = (1 - _.isna).sum()
                column_dict["n_distinct"] = distinct_col
                column_dict["duplicates"] = count_col - distinct_col
                column_dict["distinct_frac"] = distinct_col / count_col

            if descriptive_stats:
                column_dict["avg"] = (
                    col.mean().round(2).cast(str)
                    if hasattr(type_col, "mean")
                    else none_col
                )
                column_dict["max"] = (
                    col.max().cast(str) if hasattr(type_col, "max") else none_col
                )
                column_dict["min"] = (
                    col.min().cast(str) if hasattr(type_col, "min") else none_col
                )

            agg = agg.aggregate(**column_dict)

            if topk > 0:
                rename_dict[f"top_{topk}_values"] = "values"
                rename_dict[f"top_{topk}_value_counts"] = "counts"
                vc = tbl[colname].topk(topk)
                if backend is None:
                    raise ValueError("No backend found")
                elif backend.has_operation(ops.ArrayCollect):
                    vc_one_line = vc.aggregate(
                        values=getattr(vc, vc.columns[0]).cast(str).collect(),
                        counts=getattr(vc, vc.columns[1]).collect(),
                        pos=lit(pos),
                    )
                elif backend.has_operation(ops.GroupConcat):
                    vc_one_line = vc.aggregate(
                        values=getattr(vc, vc.columns[0])
                        .cast(str)
                        .group_concat(", ")
                        .name(f"top_{topk}_values"),
                        counts=getattr(vc, vc.columns[1])
                        .group_concat(", ")
                        .name(f"top_{topk}_value_counts"),
                        pos=lit(pos),
                    )
                else:
                    raise ValueError("Backend does not support topk")
                agg = agg.join(vc_one_line, "pos")
            aggs.append(agg)

        # make
        out = VinylTable(
            aggs[0]._arg if len(aggs) == 1 else ibis.union(*aggs)._arg,
            self._conn_replace,
            self._twin_conn_replace,
            self._col_replace,
        )
        if with_docs:
            docs = self._get_documentation(docs_class_name)
            out = VinylTable(
                docs.tbl.join(out.tbl, "pos")._arg,
                self._conn_replace,
                self._twin_conn_replace,
                self._col_replace,
            )
        out = out.rename(rename_dict)
        out = out.sort(out.position)

        return out

    def metric(
        self,
        cols: ir.Scalar
        | Callable[..., ir.Scalar]
        | list[ir.Scalar | Callable[..., ir.Scalar]]
        | dict[str, ir.Scalar | Callable[..., ir.Scalar]],
        ts: ir.TimestampValue | Callable[..., ir.TimestampValue],
        by: ir.Value
        | Callable[..., ir.Value]
        | Sequence[ir.Value | Callable[..., ir.Value]] = [],
        fill: FillOptions
        | Callable[..., Any] = FillOptions.null,  # all metrics have fill
    ) -> MetricStore:
        """
        Create a MetricStore (dynamic table) with a set of metrics based on the table. `cols` are the metrics, `ts` is the timestamp, `by` are the dimensions, and `fill` is the fill strategy for missing values.

        Note that this is an immutable operation, so you must assign the result to a variable to use it.

        To access the data stored in the MetricStore, use the `select` method.
        """
        from vinyl.lib.metric import MetricStore

        out = MetricStore().metric(tbl=self, cols=cols, ts=ts, by=by, fill=fill)
        if self._mutable:
            out._mutable = True
        return out

    @_ensure_output
    def _create_view(self, table_name, temporary=True):
        if not temporary:
            raise ValueError("Permanent views are not supported in Vinyl yet")

        tbl = self._execution_helper(limit=None)
        backend = _find_ibis_backends(tbl)[0]
        table = backend.create_view(
            obj=tbl,
            name=table_name
            + "\u200b",  # use invisible space to ensure no name conflicts
            overwrite=True,
        )
        return table

    @_ensure_output
    def _create_table(self, table_name, temporary=True):
        if not temporary:
            raise ValueError("Permanent views are not supported in Vinyl yet")

        tbl = self._execution_helper(limit=None)
        backend = _find_ibis_backends(tbl)[0]
        table = backend.create_table(
            obj=tbl,
            name=table_name
            + "\u200b",  # use invisible space to ensure no name conflicts
            overwrite=True,
            temp=True,
        )
        return table

    @_ensure_output
    def _alias(self, name: str) -> VinylTable:
        return self.tbl.alias(name)

    @classmethod
    def _create_from_schema(cls, schema: Schema, name: str | None = None, conn=None):
        return cls(ibis.table(schema, name=name)._arg)

    @classmethod
    def from_memory(
        cls,
        data: pd.DataFrame | pl.DataFrame | pa.Table,
    ):
        """
        Create a VinylTable from a pandas, polars, or pyarrow object
        """
        tbl = ibis.memtable(data=data)
        return VinylTable(tbl._arg)

    @classmethod
    def from_file(cls, path: str):
        """
        Create a VinylTable from a csv, json, or parquet file
        """
        filename = os.path.splitext(os.path.basename(path))[0]
        if path.endswith(".csv"):
            tbl = ibis.read_csv(path, filename)
        elif path.endswith(".json"):
            tbl = ibis.read_json(path, filename)
        elif path.endswith(".parquet"):
            tbl = ibis.read_parquet(path, filename)
        else:
            raise ValueError("File type not supported")

        return VinylTable(tbl._arg)

    def get_instance_name(self):
        for ref in gc.get_referrers(self):
            if isinstance(ref, dict):
                for k, v in ref.items():
                    if id(v) == id(self):
                        frame = inspect.currentframe()
                        while frame:
                            frame_locals = frame.f_locals
                            if k in frame_locals and frame_locals[k] is self:
                                return k
                            frame = frame.f_back
        return None  # In case no name is found

    # @lru_cache(None)
    @staticmethod
    def _get_destination(
        tbl_or_conn: ir.Table | ibis.BaseBackend, destination: tuple[str] | None = None
    ):
        if destination is None:
            raise ValueError("Destination must be provided")
        if isinstance(tbl_or_conn, ir.Table):
            backend = _find_ibis_backends(tbl_or_conn)[0]
        elif isinstance(tbl_or_conn, ibis.BaseBackend):
            backend = tbl_or_conn
        else:
            raise ValueError("tbl_or_conn must be an ibis table or backend")
        return backend.table(
            database=(destination[0], destination[1]), name=destination[2]
        )

    # The code snippet you provided is using the `@lru_cache` decorator in Python. This decorator is used
    # for memoization, which is a technique used to cache the results of function calls to avoid redundant
    # computations. In this case, `None` is passed as an argument to the `@lru_cache` decorator, which
    # means that the cache will have an unlimited size and will store all the results of function calls.
    # This can be useful for optimizing the performance of functions that are called with the same
    # arguments multiple times.
    # @lru_cache(None)
    @_ensure_output
    def sql(
        self,
        sql: str | None,
        alias: str = "t",
        simplify: bool = False,
        destination: tuple[str] | None = None,
        defer_to_destination: bool = False,
    ) -> VinylTable:
        """
        Return a VinylTable from a SQL query on a VinylTable. Note that all tables queried in the SQL must originate with self and have the same variable name as self.
        """
        y = self._execution_helper(limit=None).alias(alias)
        adj_sql = f"select * from ({sql})"  # hack for now to address cte issues in ibis

        def direct():
            if sql is None:
                raise ValueError("SQL query must be provided")
            return y.sql(adj_sql)

        def deferred():
            destination_table = self._get_destination(y, destination)
            if sql is None:
                # make an attempt to keep the flow going
                return destination_table
            return ops.SQLStringView(
                child=y.op(), query=adj_sql, schema=destination_table.schema()
            ).to_expr()

        if not defer_to_destination and destination is not None:
            try:
                out = deferred()
            except Exception:
                out = direct()
        elif destination is not None:
            try:
                out = direct()
            except Exception:
                out = deferred()
        else:
            out = direct()

        if simplify:
            out = rw.simplify(out.op()).to_expr()
        return out

    @classmethod
    def from_sql(
        cls,
        sql: str | None,
        sources: dict[str, VinylTable],
        destination: list[str] | None = None,
        defer_to_destination: bool = True,
        resource: ibis.BaseBackend | None = None,
    ) -> VinylTable:
        """
        Create a VinylTable from a SQL query.


        The sources argument should be either:
            - a dictionary with the variable name of the source table for the query as the key and the VinylTable as the value. Here's an example:
        ```
        VinylTable.from_sql(
            "select * from t cross join t2", sources= {"t": t, "t2": t2}
        )
        ```
        """
        return cls._from_sql_helper(
            sql,
            tuple(sources.items()),
            destination=tuple(destination) if destination is not None else None,
            defer_to_destination=defer_to_destination,
            resource=resource,
        )

    @classmethod
    # @lru_cache(None)
    def _from_sql_helper(
        cls,
        sql: str | None,
        sources: tuple[tuple[str, VinylTable]],
        destination: tuple[str] | None = None,
        defer_to_destination: bool = True,
        resource: ibis.BaseBackend | None = None,
    ):
        sources_dict = dict(sources)
        # raise error if you have more than one backend
        backends = []
        for k, v in sources_dict.items():
            backends_it = _find_ibis_backends(v._execution_replace(limit=None))
            backends.extend(backends_it)

        if len(set(backends)) > 1:
            raise ValueError("Multiple backends found in sources")

        new_conn_replace = {}
        new_twin_conn_replace = {}
        new_col_replace = {}
        if len(sources_dict) == 0:
            if resource is None:
                raise ValueError("No sources or connection provided")
            con = resource()._connect()
            if sql is not None:
                return VinylTable(con.sql(sql)._arg)

            if destination is None or not defer_to_destination:
                raise ValueError(
                    "Destination must be provided and defer_to_destination must be set to True if sql is None"
                )

            destination_table = cls._get_destination(con, destination)
            return VinylTable(destination_table._arg)

        if len(sources_dict) == 1:
            k, v = next(iter(sources_dict.items()))
            return v.sql(
                sql,
                alias=k,
                destination=destination if destination is not None else None,
                defer_to_destination=defer_to_destination,
                simplify=False,
            )

        for i, (k, v) in enumerate(sources_dict.items()):
            if i == 0:
                joined = v.tbl.alias(k)
            else:
                joined = joined.cross_join(v.tbl.alias(k))
            new_conn_replace.update(v._conn_replace)
            new_twin_conn_replace.update(v._twin_conn_replace)
            new_col_replace.update(v._col_replace)

        # Create joined table to ensure that all source tables have aliases registered
        joined = VinylTable(
            joined._arg, new_conn_replace, new_twin_conn_replace, new_col_replace
        )
        return joined.sql(
            sql,
            alias=_generate_random_ascii_string(10),
            simplify=False,
            destination=tuple(destination) if destination is not None else None,
            defer_to_destination=defer_to_destination,
        )  # create random alias to avoid conflict, not used in query, simplify to remove phantom cross join used for entity recognition

    @classmethod
    def get_adj_node_name(cls, n):
        if isinstance(n, VinylTable):
            # is source
            return n.get_name()
        elif hasattr(n, "_unique_name"):
            return n._unique_name
        elif hasattr(n, "_module"):
            return f"{n._module}.{n.__name__}"
        else:
            raise ValueError(f"Node {n} not recognized")


# Add pydantic validations. Need to do after function definition to make sure return class (VinylTable) is available to pydantic. Need to demote_args outside of the function to ensure validate works correctly
VinylTable.select = _demote_args(_validate(VinylTable.select))  # type: ignore[method-assign]
VinylTable.select_all = _demote_args(_validate(VinylTable.select_all))  # type: ignore[method-assign]
VinylTable.define = _demote_args(_validate(VinylTable.define))  # type: ignore[method-assign]
VinylTable.define_all = _demote_args(_validate(VinylTable.define_all))  # type: ignore[method-assign]
VinylTable.aggregate = _demote_args(_validate(VinylTable.aggregate))  # type: ignore[method-assign]
VinylTable.aggregate_all = _demote_args(_validate(VinylTable.aggregate_all))  # type: ignore[method-assign]
VinylTable.rename = _demote_args(_validate(VinylTable.rename))  # type: ignore[method-assign]
VinylTable.relocate = _demote_args(_validate(VinylTable.relocate))  # type: ignore[method-assign]
VinylTable._interpolate = _demote_args(_validate(VinylTable._interpolate))  # type: ignore[method-assign]
VinylTable.distinct = _demote_args(_validate(VinylTable.distinct))  # type: ignore[method-assign]
VinylTable.drop = _demote_args(_validate(VinylTable.drop))  # type: ignore[method-assign]
VinylTable.dropna = _demote_args(_validate(VinylTable.dropna))  # type: ignore[method-assign]
VinylTable.sort = _demote_args(_validate(VinylTable.sort))  # type: ignore[method-assign]
VinylTable.limit = _demote_args(_validate(VinylTable.limit))  # type: ignore[method-assign]
VinylTable.filter = _demote_args(_validate(VinylTable.filter))  # type: ignore[method-assign]
VinylTable.filter_all = _demote_args(_validate(VinylTable.filter_all))  # type: ignore[method-assign]
VinylTable.count = _demote_args(_validate(VinylTable.count))  # type: ignore[method-assign]
VinylTable.sample = _demote_args(_validate(VinylTable.sample))  # type: ignore[method-assign]
VinylTable.eda = _demote_args(_validate(VinylTable.eda))  # type: ignore[method-assign]
VinylTable.pivot = _demote_args(_validate(VinylTable.pivot))  # type: ignore[method-assign]
VinylTable.unpivot = _demote_args(_validate(VinylTable.unpivot))  # type: ignore[method-assign]

# Don't validate chart because its type dependencies are not imported
VinylTable.chart = _demote_args(VinylTable.chart)  # type: ignore[method-assign]
