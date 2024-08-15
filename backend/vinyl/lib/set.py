from functools import reduce, wraps
from typing import Literal

import ibis
import ibis.expr.operations as ops
import ibis.expr.types as ir

from vinyl.lib.column import _demote_args
from vinyl.lib.set_methods import (
    AUTO_JOIN_DEFAULT_HOW,
    MANUAL_JOIN_DEFAULT_HOW,
    _auto_join_helper,
    _convert_auto_join_to_ibis_join,
    base_join_type,
)
from vinyl.lib.table import VinylTable, _base_ensure_output
from vinyl.lib.table_methods import _difference_two, _intersect_two, _union_two
from vinyl.lib.utils.functions import _validate


def _ensure_output_left(func):
    @wraps(func)
    def wrapper(left: VinylTable, *args, **kwargs) -> VinylTable:
        return _base_ensure_output(func, left, *args, **kwargs)

    return wrapper


def _ensure_output_first(func):
    @wraps(func)
    def wrapper(first: VinylTable, *args, **kwargs) -> VinylTable:
        return _base_ensure_output(func, first, *args, **kwargs)

    return wrapper


@_demote_args
@_validate
@_ensure_output_left
def join(
    left: VinylTable,
    right: VinylTable,  # will be a VinylTable, but pydantic can't validate
    *args,
    auto: bool = True,
    auto_allow_cross_join: bool = False,
    on: base_join_type | list[base_join_type] = [],
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
    ]
    | None = None,
    lname: str = "",
    rname: str = "{name}_right",
    _how_override: bool = False,  # helper to determine if user has explicitly given how
) -> VinylTable:
    """
    Joins two or more tables together. if `on` is not provided and `auto` is True, the function will attempt to automatically join the tables (including multi-hop joins) based on the relationships defined in the vinyl field graph. If `on` is provided, the function will join the tables based on the provided predicates.

    If `how` is not provided, the function will default to a left join for successful auto joins and an inner join for manual joins. If `how` is provided, the function will use the specified join type. If the auto join fails, the function will raise an error unless `allow_cross_join` is set to True, in which case it will return the cross join.

    By default, all columns from the left and right tables will be included in the output. If you want to exclude columns from the right table, you can use the `select` method to select only the columns you want to keep. If there are duplicate column names in the left and right tables, lname and rname can be used to specify the suffixes to add to the column names from the left and right tables, respectively.
    """
    all_tbs = [left, right, *args]
    adj_all_tbls = []
    if not isinstance(on, list):
        on = [on]

    for tbl in all_tbs:
        if isinstance(tbl.tbl.op(), ops.UnboundTable):
            to_add = tbl._copy(
                mutable=False
            ).select(
                tbl.columns
            )  # handles issues with column replacements when joining directly to an unbound table
        else:
            to_add = tbl._copy(mutable=False)
        adj_all_tbls.append(to_add)

    if auto and on == []:
        nodes, edges = _auto_join_helper(
            adj_all_tbls, allow_cross_join=auto_allow_cross_join
        )
        first = nodes[0]
        other_nodes = nodes[1:]

        # need to ensure output to pass on all nodes into connection dicts, may be more than just left and right. We do this by making all nodes a top-level arg and using the features of ensure_output
        @_ensure_output_first
        def auto_join_iteration(first, *other_nodes, edges):
            nodes = [first, *other_nodes]
            return _convert_auto_join_to_ibis_join(
                nodes,
                edges,
                how=AUTO_JOIN_DEFAULT_HOW
                if how is None
                else how,  # uses left join unless user specifies otherwise, ignoring default
            )

        return auto_join_iteration(
            first,
            *other_nodes,
            edges=edges,
        )

    # adjust left, right, and on to ensure internal consistency
    new_left = adj_all_tbls[0].tbl
    new_right = adj_all_tbls[1].tbl
    new_on = []
    for o in on:
        if isinstance(o, ir.Expr):
            o_it = (
                o.op()
                .replace({left.tbl.op(): new_left.op(), right.tbl.op(): new_right.op()})
                .to_expr()
            )
        else:
            o_it = o
        new_on.append(o_it)

    base_join = ibis.join(
        left=new_left,
        right=new_right,
        predicates=new_on,
        how=MANUAL_JOIN_DEFAULT_HOW if how is None else how,
        lname=lname,
        rname=rname,
    )
    return base_join


@_demote_args
@_validate
@_ensure_output_first
def union(first: VinylTable, *rest: VinylTable, distinct: bool = False) -> VinylTable:
    """
    Compute the set union of multiple table expressions.

    Unlike the SQL UNION operator, this function allows for the union of tables with different schemas. If a column is present in one table but not in another, the column will be added to the other table with NULL values.

    If `distinct` is True, the result will contain only distinct rows. If `distinct` is False, the result will contain all rows from all tables, including duplicates.
    """
    if len(rest) == 0:
        return first

    return reduce(lambda x, y: _union_two(x.tbl, y.tbl, distinct), rest, first)


@_demote_args
@_validate
@_ensure_output_first
def difference(
    first: VinylTable, *rest: VinylTable, distinct: bool = False
) -> VinylTable:
    """
    Compute the set difference of multiple table expressions.

    Unlike the SQL EXCEPT operator, this function allows for the difference of tables with different schemas. If a column is present in one table but not in another, the column will be added to the other table with NULL values.

    If `distinct` is True, the result will contain only distinct rows. If `distinct` is False, the result will contain all rows from the first table, including duplicates.
    """
    if len(rest) == 0:
        return first

    return reduce(lambda x, y: _difference_two(x.tbl, y.tbl, distinct), rest, first)


@_demote_args
@_validate
@_ensure_output_first
def intersect(
    first: VinylTable, *rest: VinylTable, distinct: bool = True
) -> VinylTable:
    """
    Compute the set intersection of multiple table expressions.

    Unlike the SQL INTERSECT operator, this function allows for the intersection of tables with different schemas. If a column is present in one table but not in another, the column will be added to the other table with NULL values.

    If `distinct` is True, the result will contain only distinct rows. If `distinct` is False, the result will contain all rows that are present in all tables, including duplicates.
    """
    if len(rest) == 0:
        return first

    return reduce(lambda x, y: _intersect_two(x.tbl, y.tbl, distinct), rest, first)
