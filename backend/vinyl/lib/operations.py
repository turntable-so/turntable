from typing import Any

import ibis
from ibis.expr.types import BooleanValue, Column, IntegerColumn, IntegerValue, Value

from vinyl.lib.column import _demote_args_outside_class, _promote_output_outside_class
from vinyl.lib.utils.functions import _validate


def case(
    pairs: list[tuple[BooleanValue, Value]], default: Value | None = None
) -> Value:
    """
    Returns the first value for which the corresponding condition is true. If no conditions are true, return the default.

    Conditions should be specified as a list of tuples, where the first element of each tuple is a boolean expression and the second element is the value to return if the condition is true.
    """
    if len(pairs) == 0:
        raise ValueError("At least one pair must be provided")
    elif len(pairs) == 1:
        return ibis.ifelse(pairs[0][0], pairs[0][1], default)

    out = ibis.case()
    for pair in pairs:
        out = out.when(pair[0], pair[1])
    out = out.else_(default)
    return out.end()


def if_else(condition: Any, true_value: Any | None, false_value: Any | None) -> Value:
    """
    Constructs a conditional expression. If the condition is true, return the true_value; otherwise, return the false_value.

    Can be chained together by making the true_value or false_value another if_else expression.
    """
    return ibis.ifelse(condition, true_value, false_value)


def coalesce(*exprs) -> Value:
    """
    Return the first non-null value in the expression list.
    """
    return ibis.coalesce(*exprs)


def least(*args: Any) -> Value:
    """
    Return the smallest value among the supplied arguments.
    """
    return ibis.least(*args)


def greatest(*args: Any) -> Value:
    """
    Return the largest value among the supplied arguments.
    """
    return ibis.greatest(*args)


def row_number() -> IntegerColumn:
    """
    Returns the current row number.

    This function is normalized across backends to start from 0.
    """
    return ibis.row_number()


def rank(dense: bool = False) -> IntegerColumn:
    """
    Compute position of first element within each equal-value group in sorted order.

    If `dense` don't skip records after ties. See [here](https://learnsql.com/cookbook/whats-the-difference-between-rank-and-dense_rank-in-sql/) for a good primer on the difference.

    """
    if dense:
        return ibis.dense_rank()
    return ibis.rank()


def percent_rank() -> Column:
    """
    Compute the relative rank of a value within a group of values.
    """
    return ibis.percent_rank()


def ntile(n: int | IntegerValue) -> IntegerColumn:
    """
    Divide the rows into `n` buckets, assigning a bucket number to each row.
    """
    return ibis.ntile(n)


# Adjust the function arguments to work with VinylColumn syntax and add validation
case = _validate(_promote_output_outside_class(_demote_args_outside_class(case)))
if_else = _validate(_promote_output_outside_class(_demote_args_outside_class(if_else)))
coalesce = _validate(
    _promote_output_outside_class(_demote_args_outside_class(coalesce))
)
least = _validate(_promote_output_outside_class(_demote_args_outside_class(least)))
greatest = _validate(
    _promote_output_outside_class(_demote_args_outside_class(greatest))
)
row_number = _validate(
    _promote_output_outside_class(_demote_args_outside_class(row_number))
)
rank = _validate(_promote_output_outside_class(_demote_args_outside_class(rank)))
percent_rank = _validate(
    _promote_output_outside_class(_demote_args_outside_class(percent_rank))
)
ntile = _validate(_promote_output_outside_class(_demote_args_outside_class(ntile)))
