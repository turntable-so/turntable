from __future__ import annotations

from typing import Any, Callable, Literal, Sequence, TypeAlias

import ibis
import ibis.expr.operations as ops
import ibis.expr.types as ir
from ibis import _
from ibis import selectors as s
from ibis.common.deferred import Deferred
from vinyl.lib.column import VinylColumn
from vinyl.lib.column_methods import (
    ColumnListBuilder,
    base_column_type,
    column_type_all,
)
from vinyl.lib.enums import FillOptions
from vinyl.lib.utils.text import _generate_random_ascii_string

fill_type: TypeAlias = (
    list[FillOptions | Callable[..., Any] | None]
    | FillOptions
    | Callable[..., Any]
    | None
)


def _expand_col(
    tbl: ir.Table, col: ir.Value, adjust_name: bool = False
) -> tuple[ir.Table, dict[str, str | None] | None]:
    vinyl_col = ColumnListBuilder(tbl, col)
    cur_col_name = vinyl_col._names[0]
    type_ = vinyl_col._types[0]
    col_key = "col_it"
    col_tbl = tbl.select(vinyl_col._queryable)
    default_return = col_tbl.distinct()

    if type_ is None or (not type_.is_timestamp() and not type_.is_date()):
        return default_return, None

    if isinstance(col, Deferred):
        col = col.resolve(tbl)
    col_op = col.op()
    last_fn_list = col_op.find_topmost(ops.TimestampBucket) + col_op.find_topmost(
        ops.TimestampTruncate
    )
    last_fn = last_fn_list[0] if len(last_fn_list) > 0 else None
    original_col = ColumnListBuilder(tbl, col_op.find_topmost(ops.Field)[0].to_expr())
    new_col_name = original_col._names[0] if adjust_name else None

    if last_fn is None:
        return default_return, None

    temp_renamed_col_tbl = col_tbl.rename({col_key: cur_col_name})

    range_helper = temp_renamed_col_tbl.aggregate(
        metrics=[
            getattr(_, col_key).min().name("min"),
            getattr(_, col_key).max().name("max"),
        ]
    )
    sel_name = new_col_name if new_col_name is not None else cur_col_name
    sel_name_for_rename_dict: dict[str, str | None] = (
        {cur_col_name: new_col_name}
        if new_col_name is not None and cur_col_name is not None
        else {}
    )

    if type_.is_timestamp():
        if isinstance(last_fn, ops.TimestampTruncate):
            range_ = (
                ops.TimestampRange(
                    start=range_helper.min,
                    stop=range_helper.max
                    + ibis.interval(
                        unit=last_fn.unit, value=1
                    ),  # need inclusive range, ibis stop is exclusive by default
                    step=ibis.interval(unit=last_fn.unit, value=1),
                )
                .to_expr()
                .name(sel_name)
                .as_table()
                .select(_[sel_name].unnest())
            )
            return ir.Table(range_._arg), sel_name_for_rename_dict

        elif isinstance(last_fn, ops.TimestampBucket):
            range_ = (
                ops.TimestampRange(
                    start=range_helper.min,
                    stop=range_helper.max
                    + last_fn.interval,  # need inclusive range, ibis stop is exclusive by default
                    step=last_fn.interval,
                )
                .to_expr()
                .name(sel_name)
                .as_table()
                .select(_[sel_name].unnest())
            )
            return ir.Table(range_._arg), sel_name_for_rename_dict

        else:
            return default_return, None

    return default_return, None


def _auto_join(tbl: ir.Table, tbl2: ir.Table) -> ir.Table:
    common_columns = list(set(tbl.schema().names) & set(tbl2.schema().names))
    if len(common_columns) == 0:
        return tbl.cross_join(tbl2)
    else:
        return tbl.outer_join(tbl2, predicates=common_columns)


def _build_spine(
    tbl: ir.Table, cols: Sequence[ir.Scalar]
) -> tuple[ir.Table, dict[str, Any] | None]:
    # no need to go through expansion logic if there is only one column and there's no interpolation
    vinyl_cols = ColumnListBuilder(tbl, cols)
    if len(vinyl_cols._cols) == 1:
        return _expand_col(tbl, vinyl_cols._queryable[0])

    rename_dict = {}
    zipped = list(zip(vinyl_cols._names, vinyl_cols._queryable))
    for i, (name, col) in enumerate(zipped):
        expanded_col_tpl = _expand_col(tbl, col)
        if expanded_col_tpl[1]:
            rename_dict.update(expanded_col_tpl[1])

        if i == 0:
            spine = expanded_col_tpl[0]
        else:
            spine = _auto_join(spine, expanded_col_tpl[0])

    return spine, rename_dict


def _join_spine(self, spine: ir.Table) -> ir.Table:
    # generate random col_name to remove extra join columns (ibis includes all cols from left and right by default)
    random_col_suffix = _generate_random_ascii_string()
    rname = f"{{name}}_{random_col_suffix}"

    null_fill = spine.left_join(  # ensure using ibis join
        self,
        predicates=[(spine[n], self[n]) for n in spine.schema().names],
        rname=rname,
    ).drop(s.contains(random_col_suffix))  # perform the drop

    return null_fill


def _adjust_fill_list(
    n_col: int,
    fill: list[FillOptions | Callable[..., Any] | None]
    | FillOptions
    | Callable[..., Any]
    | None = None,
) -> list[FillOptions | Callable[..., Any] | None]:
    fill_list: list[FillOptions | Callable[..., Any] | None]
    if isinstance(fill, FillOptions):
        fill_list = [fill] * n_col
    elif isinstance(fill, list):
        fill_list = fill
    else:
        # is a lambda
        fill_list = [fill] * n_col

    if len(fill_list) != n_col:
        raise ValueError(
            "Must provide either a single fill option or a fill option for each aggregation"
        )

    return fill_list


def _union_adjuster(
    first: ir.Table, second: ir.Table, distinct: bool = False
) -> ir.Table:
    # get current schemas
    first_schema = first.schema()
    first_names = first_schema.names
    second_schema = second.schema()
    second_names = second_schema.names

    # check if any common cols have different types, raise error if they do
    common_cols = set(first_names) & set(second_names)
    common_cols_with_diff_types = [
        col for col in common_cols if first_schema[col] != second_schema[col]
    ]
    if len(common_cols_with_diff_types) > 0:
        raise ValueError(
            f"Cannot union tables with common columns of different types: {common_cols_with_diff_types}"
        )
    # get correct column order (self + other not in self)
    all_cols_with_duplicates = first_names + second_names
    all_cols = list(set(all_cols_with_duplicates))

    # if no columns to add, return union
    if (
        len(all_cols_with_duplicates)
        == len(first_schema.names)
        == len(all_cols_with_duplicates)
    ):
        return first.union(second, distinct=distinct)

    # get columns to add
    self_cols_to_add = [
        ibis.NA.cast(second_schema[col]).name(col)
        for col in all_cols
        if col not in first_schema.names
    ]
    other_cols_to_add = [
        ibis.NA.cast(first_schema[col]).name(col)
        for col in all_cols
        if col not in second_schema.names
    ]

    # add missing columns to each table
    adjusted_first_cols = [getattr(_, name) for name in first_names] + self_cols_to_add
    adjusted_first = (
        first.select(*adjusted_first_cols) if len(self_cols_to_add) > 0 else first
    )
    adjusted_second_cols = [
        getattr(_, name) for name in second_names
    ] + other_cols_to_add
    adjusted_second = (
        second.select(*adjusted_second_cols) if len(other_cols_to_add) > 0 else second
    )

    return adjusted_first, adjusted_second


def _union_two(first: ir.Table, second: ir.Table, distinct: bool = False) -> ir.Table:
    adjusted_first, adjusted_second = _union_adjuster(first, second, distinct)
    return adjusted_first.union(adjusted_second, distinct=distinct)


def _difference_two(
    first: ir.Table, second: ir.Table, distinct: bool = False
) -> ir.Table:
    adjusted_first, adjusted_second = _union_adjuster(first, second, distinct)
    return adjusted_first.difference(adjusted_second, distinct=distinct)


def _intersect_two(
    first: ir.Table, second: ir.Table, distinct: bool = True
) -> ir.Table:
    adjusted_first, adjusted_second = _union_adjuster(first, second, distinct)
    return adjusted_first.intersect(adjusted_second, distinct=distinct)


def _join_with_removal(
    self: ir.Table,
    other: ir.Table,
    how: Literal[
        "inner",
        "left",
        "outer",
        "right",
        "semi",
        "anti",
        "any_inner",
        "any_left",
        "left_semi",
    ] = "outer",
) -> ir.Table:
    random_col_suffix = _generate_random_ascii_string()
    rname = f"{{name}}_{random_col_suffix}"
    common_columns = list(set(self.columns) & set(other.columns))
    if len(common_columns) == 0:
        return self.cross_join(other)
    else:
        return self.join(other, predicates=common_columns, rname=rname, how=how).drop(
            s.contains(random_col_suffix)
        )


def _select_process_helper(tbl: ir.Table, se: base_column_type):
    name_dict = {}
    vinyl_se = ColumnListBuilder(tbl, se)
    if isinstance(se, s.Selector):
        name_dict = {col._name: col._col for col in vinyl_se._cols}

    else:
        cur_name = vinyl_se._names[0]
        sources = vinyl_se._get_direct_col_sources(unique=False)[0]
        adj_name = sources[0] if sources != [] else cur_name
        name_dict[adj_name] = se

    return name_dict


def _process_multiple_select(
    tbl: ir.Table,
    col_selector: column_type_all,
    f: Callable[[Any], Any] | list[Callable[[Any], Any] | None] | None,
    rename=True,
) -> list[ir.Value]:
    col_selector_list = (
        [col_selector] if not isinstance(col_selector, list) else col_selector
    )
    f_list: list[Callable[..., Any] | None] = [f] if not isinstance(f, list) else f

    if len(f_list) == 1 and len(col_selector_list) > 1:
        f_list = f_list * len(col_selector_list)

    if len(col_selector_list) != len(f_list):
        raise ValueError(
            "Must provide either a single function or a function for each column or selector"
        )

    adj_cols = []
    # make sure col_selector is enumerable
    if isinstance(col_selector, (str, s.Selector, ir.Value)) or callable(col_selector):
        col_selector = [col_selector]
    for i, sel in enumerate(col_selector):
        name_dict = {}
        if isinstance(sel, list):
            for se in sel:
                name_dict.update(_select_process_helper(tbl, se))
        else:
            name_dict.update(_select_process_helper(tbl, sel))

        for name, col in name_dict.items():
            f_it = f_list[i]  # extra step to help mypy
            if not isinstance(col, VinylColumn):
                col = VinylColumn(col)
            if f_it is not None:
                core = f_it(col)
            else:
                core = col
            core = core._col.name(name) if not rename else core._col
            adj_cols.append(core)

    return adj_cols


def _find_ibis_backends(tbl: ir.Table) -> ibis.BaseBackend:
    return [be for be in tbl._find_backends()[0] if isinstance(be, ibis.BaseBackend)]
