# used for autocomplete for VinylTable and MetricStore classes
from __future__ import annotations

from collections.abc import Iterable, Sequence
from functools import wraps
from typing import Any, Callable, Literal

import ibis
import ibis.expr.operations as ops
from ibis.common.deferred import Deferred
from ibis.expr.datatypes import DataType
from ibis.expr.types import (
    ArrayColumn,
    ArrayValue,
    BooleanValue,
    Column,
    DateValue,
    Expr,
    IntegerValue,
    IntervalValue,
    MapColumn,
    NumericValue,
    Scalar,
    StringColumn,
    StringValue,
    StructColumn,
    TimestampValue,
    Value,
)


# self excluded to avoid recursion
def _promote_output(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if isinstance(result, Value):
            return VinylColumn(result)
        return result

    return wrapper


def _promote_output_outside_class(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, Value):
            return VinylColumn(result)
        return result

    return wrapper


def _adj_args_and_output(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        new_args = []
        for i, arg in enumerate(args):
            new_args.append(_demote_arg(arg))
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = _demote_arg(v)
        return func(self, *new_args, **new_kwargs)

    return wrapper


# Class decorator that applies the function decorator to all methods
def _transform_all_methods(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value):
            setattr(cls, attr_name, _promote_output(_adj_args_and_output(attr_value)))
    return cls


@_transform_all_methods
class VinylColumn:
    _col: Value
    array: VinylColumn.ArrayFunctions
    math: VinylColumn.MathFunctions
    url: VinylColumn.URLFunctions
    re: VinylColumn.RegexFunctions
    str: VinylColumn.StringFunctions
    dict: VinylColumn.MapFunctions
    obj: VinylColumn.StructFunctions
    dt: VinylColumn.TemporalFunctions

    ## dunders not implemented: __complex__, __format__, __getslice__ (deprecated), __index__, __matmul__, __rmatmul__
    ## dunders that could be implemented but not yet: __reversed__
    def __init__(self, _col: Column):
        self._col = _col
        self.array = self.ArrayFunctions()  # type: ignore[call-arg]
        self.math = self.MathFunctions()  # type: ignore[call-arg]
        self.url = self.URLFunctions()  # type: ignore[call-arg]
        self.re = self.RegexFunctions()  # type: ignore[call-arg]
        self.str = self.StringFunctions()  # type: ignore[call-arg]
        self.dict = self.MapFunctions()  # type: ignore[call-arg]
        self.obj = self.StructFunctions()  # type: ignore[call-arg]
        self.dt = self.TemporalFunctions()  # type: ignore[call-arg]

    def __repr__(self) -> str:  # type: ignore[valid-type]
        return self._col.__repr__()

    def __str__(self) -> str:  # type: ignore[valid-type]
        return self._col.__str__()

    # not implemented by ibis, but adding here
    def __abs__(self) -> VinylColumn:
        return self._col.abs()

    def __add__(self, other: Any) -> VinylColumn:
        return type(self._col).__add__(self._col, other)

    def __and__(self, other: Any) -> VinylColumn:
        if isinstance(self._col, ArrayColumn):
            return self._col.intersect(other)
        return type(self._col).__and__(self._col, other)

    def __bool__(self) -> VinylColumn:
        return type(self._col).__bool__(self._col)

    # not implemented by ibis, but adding here
    def __ceil__(self) -> VinylColumn:
        return self._col.ceil()

    def __cmp__(self, other: Any) -> VinylColumn:
        # using ibis ifelse here to avoid recursion
        return ibis.ifelse(self._col == other, 0, ibis.ifelse(self._col < other, -1, 1))

    def __contains__(self, key: Any) -> VinylColumn:
        return type(self._col).__contains__(self._col, key)

    def __divmod__(self, other: Any) -> VinylColumn:
        return type(self._col).__divmod__(self._col, other)

    def __eq__(self, other: Any) -> VinylColumn:  # type: ignore
        if other is None:
            return self._col.isnull()
        return type(self._col).__eq__(self._col, other)  # type: ignore

    # not implemented by ibis, but adding here
    def __float__(self) -> VinylColumn:
        return self._col.cast(float)

    # not implemented by ibis, but adding here
    def __floor__(self) -> VinylColumn:
        return self._col.floor()

    def __floordiv__(self, other: Any) -> VinylColumn:
        return type(self._col).__floordiv__(self._col, other)

    def __ge__(self, other: Any) -> VinylColumn:
        return type(self._col).__ge__(self._col, other)

    def __getitem__(self, key: Any) -> VinylColumn:
        if not isinstance(self._col, StringColumn):
            return type(self._col).__getitem__(self._col, key)

        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step

            if not isinstance(start, (Expr, VinylColumn)):
                if start is not None and start < 0:
                    start = self._col.length() + start

            if not isinstance(stop, (Expr, VinylColumn)):
                if stop is not None and stop < 0:
                    stop = self._col.length() + stop

            if step == -1:
                adj_stop = self._col.length() - start - 1 if start is not None else None
                adj_start = self._col.length() - stop - 1 if stop is not None else None
                return VinylColumn(self._col.reverse()).__getitem__(
                    slice(adj_start, adj_stop, 1)
                )

            if start is None:
                start = 0
            if stop is None:
                stop = self._col.length()

                if stop is None:
                    stop = self._col.length()

            if step is not None and not isinstance(step, Expr) and abs(step) != 1:
                raise ValueError("Step can only be 1 or -1 for string slicing")

            return self.str.substr(start, stop - start)

        elif isinstance(key, int):
            return self.str.substr(key, 1)
        raise NotImplementedError(f"string __getitem__[{key.__class__.__name__}]")

    def __gt__(self, other: Any) -> VinylColumn:
        return type(self._col).__gt__(self._col, other)

    def __hash__(self) -> VinylColumn:  # type: ignore
        return type(self._col).__hash__(self._col)  # type: ignore

    # not implemented by ibis, but adding here
    def __int__(self) -> VinylColumn:
        return self._col.cast(int)

    def __invert__(self) -> VinylColumn:
        return type(self._col).__invert__(self._col)

    def __iter__(self) -> VinylColumn:
        return type(self._col).__iter__(self._col)

    def __le__(self, other: Any) -> VinylColumn:
        return type(self._col).__le__(self._col, other)

    # doesn't really work, because python requires len to return an integer
    def __len__(self) -> VinylColumn:
        return type(self._col).__len__(self._col)

    def __lshift__(self, other: Any) -> VinylColumn:
        return type(self._col).__lshift__(self._col, other)

    def __lt__(self, other: Any) -> VinylColumn:
        return type(self._col).__lt__(self._col, other)

    def __mod__(self, other: Any) -> VinylColumn:
        return type(self._col).__mod__(self._col, other)

    def __mul__(self, other: Any) -> VinylColumn:
        return type(self._col).__mul__(self._col, other)

    def __ne__(self, other: Any) -> VinylColumn:  # type: ignore
        if other is None:
            return self._col.notnull()
        return type(self._col).__ne__(self._col, other)  # type: ignore

    def __neg__(self) -> VinylColumn:
        # helps with sorting behavior
        if not hasattr(type(self._col), "__neg__"):
            # turn this into a negated sort key
            return ops.SortKey(self._col.op(), ascending=False).to_expr()

        # sort key conversion will be handled later, and this prevents issues with negating numerics, etc.
        return type(self._col).__neg__(self._col)

    # likely not implemented, but including just in case
    def __next__(self) -> VinylColumn:
        return type(self._col).__next__(self._col)

    def __nonzero__(self) -> VinylColumn:
        return type(self._col).__nonzero__(self._col)

    def __or__(self, other: Any) -> VinylColumn:  # type: ignore
        if isinstance(self._col, ArrayColumn) and isinstance(other, ArrayColumn):
            return self._col.union(other)
        return type(self._col).__or__(self._col, other)  # type: ignore

    # not implemented by ibis, but adding here
    def __pos__(self) -> VinylColumn:
        return self._col

    def __pow__(self, other: Any) -> VinylColumn:
        return type(self._col).__pow__(self._col, other)

    def __radd__(self, other: Any) -> VinylColumn:
        return type(self._col).__radd__(self._col, other)

    def __rand__(self, other: Any) -> VinylColumn:
        return type(self._col).__rand__(self._col, other)

    def __rdiv__(self, other: Any) -> VinylColumn:
        return type(self._col).__rdiv__(self._col, other)

    def __rdivmod__(self, other: Any) -> VinylColumn:
        return type(self._col).__rdivmod__(self._col, other)

    def __rfloordiv__(self, other: Any) -> VinylColumn:
        return type(self._col).__rfloordiv__(self._col, other)

    def __rlshift__(self, other: Any) -> VinylColumn:
        return type(self._col).__rlshift__(self._col, other)

    def __rmul__(self, other: Any) -> VinylColumn:
        return type(self._col).__rmul__(self._col, other)

    def __ror__(self, other: Any) -> VinylColumn:  # type: ignore
        return type(self._col).__ror__(self._col, other)  # type: ignore

    # not implemented by ibis, but adding here
    def __round__(self, ndigits: Any) -> VinylColumn:
        return self._col.round(ndigits)

    def __rpow__(self, other: Any) -> VinylColumn:
        return type(self._col).__rpow__(self._col, other)

    def __rrshift__(self, other: Any) -> VinylColumn:
        return type(self._col).__rrshift__(self._col, other)

    def __rshift__(self, other: Any) -> VinylColumn:
        return type(self._col).__rshift__(self._col, other)

    def __rsub__(self, other: Any) -> VinylColumn:
        return type(self._col).__rsub__(self._col, other)

    def __rtruediv__(self, other: Any) -> VinylColumn:
        return type(self._col).__rtruediv__(self._col, other)

    def __rxor__(self, other: Any) -> VinylColumn:
        return type(self._col).__rxor__(self._col, other)

    def __sub__(self, other: Any) -> VinylColumn:
        return type(self._col).__sub__(self._col, other)

    def __truediv__(self, other: Any) -> VinylColumn:
        return type(self._col).__truediv__(self._col, other)

    # not implemented by ibis, but adding here
    def __trunc__(self):
        return ibis.ifelse(self._col < 0, self._col.floor(), self._col.ceil())

    def __xor__(self, other: Any) -> VinylColumn:
        return type(self._col).__xor__(self._col, other)

    def between(self, lower: Value, upper: Value) -> VinylColumn:
        """
        Check if this expression is between lower and upper, inclusive.
        """
        return VinylColumn(self._col.between(lower, upper))

    def match(
        self, case_pairs: list[tuple[BooleanValue, Value]], default: Value | None = None
    ) -> Value:
        """
        Return a value based on the first matching condition in the expression. The default value is returned if no conditions are met, otherwise null is returned.
        """
        out = self._col.case()
        for pair in case_pairs:
            out = out.when(pair[0], pair[1])
        if default is not None:
            out = out.else_(default)

        return out

    def cast(self, target_type: Any, try_: bool = False) -> Value:
        """
        Cast expression to indicated data type. Type inputs can include strings, python type annotations, numpy dtypes, pandas dtypes, and pyarrow dtypes.

        If try_ is True, then the cast will return null if the cast fails, otherwise it will raise an error.
        """
        if try_:
            return self._col.try_cast(target_type)
        return self._col.cast(target_type)

    def coalesce(self, *args: Value) -> Value:
        """
        Return the first non-null value in the expression list.
        """
        return ibis.coalesce(self._col, *args)

    def fillna(self, value: Value) -> Value:
        """
        Replace null values in the expression with the specified value.
        """
        return self._col.fillna(value)

    def hash(self) -> IntegerValue:
        """
        Compute an integer hash value of the expression.

        The hashing function used is dependent on the backend, so usage across dialect will likely return a different number.
        """
        return self._col.hash()

    def equivalent(self, other: Value) -> BooleanValue:
        """
        Null-aware version of ==. Returns true if both expressions are equal or both are null.
        """
        return self._col.identical_to(other)

    def isin(self, values: Value | Sequence[Value]) -> BooleanValue:
        """
        Check if this expression is in the provided set of values. Exists in place of the python `in` operator because of its requirement to evaluate to a python boolean.
        """
        return self._col.isin(values)

    def type(self, db_type: bool = True) -> DataType | IntegerValue:
        """
        Return the string name of the datatype of the expression.

        If db_type is True, then the string will be the name of the datatype in the specific backend (e.g. duckdb), otherwise it will be cross-dialect data type name from Vinyl.
        """
        if db_type:
            return self._col.typeof()
        return self._col.type()

    def median(self, where: BooleanValue | None = None, approx: bool = False) -> Scalar:
        """
        Return the median value of the expression.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.

        If `approx` is True, method will use the approximate median function, which is faster but less accurate.
        """
        if approx:
            return self._col.approx_median(where)
        return self._col.median(where)

    def count(
        self,
        where: BooleanValue | None = None,
        distinct: bool = False,
        approx: bool = False,
    ) -> Scalar:
        """
        Return the number of non-null values in the expression, only including values when the `where` condition is true.

        If `distinct` is True, then the number of unique values will be returned instead of the total count.

        If `approx` is True and `distinct` is True, method will use approximate count distinct function, which is faster but less accurate. This is only available for count distinct.
        """
        if distinct:
            if approx:
                return self._col.approx_nunique(where)
            else:
                return self._col.nunique(where)
        return self._col.count(where)

    def argmin(self, key: Value, where: BooleanValue | None = None) -> Scalar:
        """
        Return the value of key when the expression is at its minimum value.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.argmin(where)

    def argmax(self, key: Value, where: BooleanValue | None = None) -> Scalar:
        """
        Return the value of key when the expression is at its maximum value.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.argmax(where)

    def as_scalar(self) -> Scalar:
        """
        Convert the expression to a scalar value. Note that the execution of the scalar subquery will fail if the column expression contains more than one value.
        """
        return self._col.as_scalar()

    def first(self, where: BooleanValue | None = None) -> Scalar:
        """
        Return the first value in the expression.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.first(where)

    def last(self, where: BooleanValue | None = None) -> Scalar:
        """
        Return the last value in the expression.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.last(where)

    def lag(
        self, offset: int | IntegerValue | None = None, default: Value | None = None
    ) -> Scalar:
        """
        Return the row located at offset rows before the current row. If no row exists at offset, the default value is returned.
        """
        return self._col.lag(offset, default)

    def lead(
        self, offset: int | IntegerValue | None = None, default: Value | None = None
    ) -> Scalar:
        """
        Return the row located at offset rows after the current row. If no row exists at offset, the default value is returned.
        """
        return self._col.lead(offset, default)

    def max(self, where: BooleanValue | None = None) -> Scalar:
        """
        Return the maximum value of the expression

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.max(where)

    def min(self, where: BooleanValue | None = None) -> Scalar:
        """
        Return the minimum value of the expression

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.min(where)

    def mode(self, where: BooleanValue | None = None) -> Scalar:
        """
        Return the mode value of the expression

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.mode(where)

    def nth(self, n: int | IntegerValue) -> Scalar:
        """
        Return the nth value of the expression
        """
        return self._col.nth(n)

    def quantile(
        self,
        quantiles: float | NumericValue | list[NumericValue | float],
        where: BooleanValue | None = None,
    ) -> Scalar:
        """
        Return value at the given quantile. If multiple quantiles are specified, then the output will be an array of values.

        The output of this method a discrete quantile if the input is an float, otherwise it is a continuous quantile.
        """
        return self._col.quantile(quantiles, where)

    def like(
        self,
        patterns: str | StringValue | Iterable[str | StringValue],  # type: ignore[valid-type]
        case_sensitive: bool = True,
    ) -> BooleanValue:
        """
        This function is modeled after SQL's `LIKE` and `ILIKE` directives. Use `%` as a
        multiple-character wildcard or `_` as a single-character wildcard.

        For regular expressions, use `re.search`.
        """
        if case_sensitive:
            return self._col.like(patterns)
        return self._col.ilike(patterns)

    def combine(self, sep: str = ", ", where=None) -> Value:  # type: ignore[valid-type]
        """
        Combine the expression into a single string using the specified separator.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.group_concat(sep, where)

    def collect(self, where: BooleanValue | None = None) -> ArrayColumn:
        """
        Collect the expression into an array.

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.collect()

    def sum(self, where: BooleanValue | None = None) -> VinylColumn:
        """
        Return the sum of the expression

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.sum(where)

    def mean(self, where: BooleanValue | None = None) -> VinylColumn:
        """
        Return the mean of the expression

        If a `where` condition is specified, method only considers rows meeting the `where` condition.
        """
        return self._col.mean(where)

    # inner classes
    @_transform_all_methods
    class MathFunctions:
        _col: NumericValue

        def __init__(self, col: Column):
            self._col = col

        def fabs(self) -> VinylColumn:
            """
            Return the absolute value of the expression.
            """
            return self._col.abs()

        def acos(self) -> VinylColumn:
            """
            Return the arc cosine of the expression.
            """
            return self._col.acos()

        def asin(self) -> VinylColumn:
            """
            Return the arc sine of the expression.
            """
            return self._col.asin()

        def atan(self) -> VinylColumn:
            """
            Return the arc tangent of the expression.
            """
            return self._col.atan()

        def atan2(self, other: NumericValue) -> VinylColumn:
            """
            Return the two-argument arc tangent of the expression.
            """
            return self._col.atan2(other)

        def ceil(self) -> VinylColumn:
            """
            Return the smallest integer value not less than the expression.
            """
            return self._col.ceil()

        def cos(self) -> VinylColumn:
            """
            Return the cosine of the expression.
            """
            return self._col.cos()

        def cot(self) -> VinylColumn:
            """
            Return the cotangent of the expression.
            """
            return self._col.cot()

        def degrees(self) -> VinylColumn:
            """
            Convert radians to degrees.
            """
            return self._col.degrees()

        def exp(self) -> VinylColumn:
            """
            Return the expression raised to the power of e.
            """
            return self._col.exp()

        def floor(self) -> VinylColumn:
            """
            Return the largest integer value not greater than the expression.
            """
            return self._col.floor()

        def log(self, base: NumericValue | None = None) -> VinylColumn:
            """
            Return the logarithm of the expression. If base is specified, then the logarithm will be taken to that base. Otherwise, the natural logarithm is taken.
            """
            return self._col.log(base)

        def log10(self) -> VinylColumn:
            """
            Return the base-10 logarithm of the expression.
            """
            return self._col.log10()

        def log2(self) -> VinylColumn:
            """
            Return the base-2 logarithm of the expression.
            """
            return self._col.log2()

        def radians(self) -> VinylColumn:
            """
            Convert degrees to radians.
            """
            return self._col.radians()

        def round(self, digits: int | IntegerValue | None = None) -> VinylColumn:
            """
            Round the expression to the specified number of decimal places. If digits is not specified, then the expression is rounded to the nearest integer.
            """
            return self._col.round(digits)

        def sign(self) -> VinylColumn:
            """
            Return the sign of the expression.
            """
            return self._col.sign()

        def sin(self) -> VinylColumn:
            """
            Return the sine of the expression.
            """
            return self._col.sin()

        def sqrt(self) -> VinylColumn:
            """
            Return the square root of the expression.
            """
            return self._col.sqrt()

        def tan(self) -> VinylColumn:
            """
            Return the tangent of the expression.
            """
            return self._col.tan()

        # math library functions added

        def copysign(self, other: NumericValue) -> VinylColumn:
            """
            Return the expression with the sign of the other expression.
            """
            return abs(self._col) * self._col.sign(other)

        def isclose(
            self, other: NumericValue, rel_tol: float = 1e-09, abs_tol: float = 0.0
        ) -> VinylColumn:
            """
            Return True if the values are close to each other and False otherwise.
            """
            return abs(self._col - other) <= max(
                rel_tol * max(abs(self._col), abs(other)), abs_tol
            )

        def isqrt(self) -> VinylColumn:
            """
            Return the integer square root of the expression.
            """
            return self._col.sqrt().floor()

        def ldexp(self, other: NumericValue) -> VinylColumn:
            """
            Return the expression multiplied by 2 to the power of the other expression.
            """
            return self._col * (2**other)

        def modf(self) -> VinylColumn:
            """
            Return the fractional and integer parts of the expression.
            """

            return VinylColumn([self._col - self._col.floor(), self._col.floor()])

        def prod(self, *args: NumericValue) -> VinylColumn:
            """
            Return the product of the expression and the other expressions.
            """
            out = self._col
            for arg in args:
                out *= arg
            return out

        def remainder(self, other: int | IntegerValue) -> VinylColumn:
            """
            Return the remainder of the expression divided by the other expression.
            """
            return self._col % other

        def sumprod(self, other: NumericValue) -> VinylColumn:
            """
            Return the sum of the product of the expression and the other expression.
            """
            return (self._col * other).sum()

        def trunc(self) -> VinylColumn:
            """
            Return the truncated value of the expression.
            """
            return self._col.trunc()

        def cbrt(self) -> VinylColumn:
            """
            Return the cube root of the expression.
            """
            return self._col ** (1 / 3)

        def exp2(self) -> VinylColumn:
            """
            Return 2 raised to the power of the expression.
            """
            return 2**self._col

        def expm1(self) -> VinylColumn:
            """
            Return e raised to the power of the expression minus 1.
            """
            return self._col.exp() - 1

        def pow(self, other: NumericValue) -> VinylColumn:
            """
            Return the expression raised to the power of the other expression.
            """
            return self._col**other

        def norm(self, type_: Literal["L1", "L2"] = "L2") -> VinylColumn:
            """
            Return the L2 norm of the expression.
            """
            if type_ == "L2":
                return (self._col**2).sum().sqrt()
            elif type_ == "L1":
                return self._col.abs().sum()
            else:
                raise ValueError("Invalid norm type")

        def dist(
            self,
            other: NumericValue,
            type_: Literal["Euclidian", "Manhattan", "Cosine"],
        ) -> VinylColumn:
            """
            Return the distance between the expression and the other expression.
            """
            if type_ == "Euclidian":
                return (self - VinylColumn(other)).math.norm("L2")

            if type_ == "Manhattan":
                return (self._col - VinylColumn(other)).math.norm("L1")

            if type_ == "Cosine":
                return (self._col * other).sum() / (
                    self.norm("L2") * VinylColumn(other).math.norm("L2")
                )

        def acosh(self) -> VinylColumn:
            """
            Return the inverse hyperbolic cosine of the expression.
            """
            return (self._col + (self._col**2 - 1).sqrt()).log()

        def asinh(self) -> VinylColumn:
            """
            Return the inverse hyperbolic sine of the expression.
            """
            return (self._col + (self._col**2 + 1).sqrt()).log()

        def atanh(self) -> VinylColumn:
            """
            Return the inverse hyperbolic tangent of the expression.
            """
            return ((1 + self._col) / (1 - self._col)).log() / 2

        def cosh(self) -> VinylColumn:
            """
            Return the hyperbolic cosine of the expression.
            """
            return (self._col.exp() + (-self._col).exp()) / 2

        def sinh(self) -> VinylColumn:
            """
            Return the hyperbolic sine of the expression.
            """
            return (self._col.exp() - (-self._col).exp()) / 2

        def tanh(self) -> VinylColumn:
            """
            Return the hyperbolic tangent of the expression.
            """
            return self.sinh() / self.cosh()

    @_transform_all_methods
    class URLFunctions:
        _col: StringValue

        def __init__(self, col: VinylColumn):
            self._col = col

        def authority(self) -> VinylColumn:
            """
            Return the authority of the expression.
            """
            return self._col.authority()

        def file(self) -> VinylColumn:
            """
            Parse a URL and extract the file.
            """
            return self._col.file()

        def fragment(self) -> VinylColumn:
            """
            Parse a URL and extract fragment identifier.
            """
            return self._col.fragment()

        def host(self) -> VinylColumn:
            """
            Parse a URL and extract the host.
            """
            return self._col.host()

        def path(self) -> VinylColumn:
            """
            Parse a URL and extract the path.
            """
            return self._col.path()

        def protocol(self) -> VinylColumn:
            """
            Parse a URL and extract the protocol.
            """
            return self._col.protocol()

        def query(self, key: str | StringValue | None = None) -> VinylColumn:
            """
            Parse a URL and extract the query string. If a key is specified, then the value of that key is returned. Otherwise, the entire query string is returned.
            """
            return self._col.query(key)

        def userinfo(self) -> VinylColumn:
            """
            Parse a URL and extract the userinfo.
            """
            return self._col.userinfo()

    @_transform_all_methods
    class RegexFunctions:
        _col: StringValue

        def __init__(self, col: VinylColumn):
            self._col = col

        def extract(
            self, pattern: str | StringValue, index: int | IntegerValue
        ) -> VinylColumn:
            """
            Return the specified match at index from a regex pattern.

            The behavior of this function follows the behavior of Python’s match objects: when index is zero and there’s a match, return the entire match, otherwise return the content of the index-th match group.
            """
            return self._col.re_extract(pattern, index)

        def replace(
            self, pattern: str | StringValue, replacement: str | StringValue
        ) -> VinylColumn:
            """
            Replace the matches of a regex pattern with a replacement string.
            """
            return self._col.re_replace(pattern, replacement)

        def search(self, pattern: str | StringValue) -> VinylColumn:
            """
            Returns True if the regex pattern matches a string and False otherwise.
            """
            return self._col.re_search(pattern)

        def split(self, pattern: str | StringValue) -> VinylColumn:
            """
            Split the expression using a regex pattern.
            """
            return self._col.re_split(pattern)

    @_transform_all_methods
    class StringFunctions:
        _col: StringValue

        def __init__(self, col: VinylColumn):
            self._col = col

        def ord(self) -> VinylColumn:
            """
            Return the unicode code point of the first character of the expression.
            """
            return self._col.ascii_str()

        def capitalize(self) -> VinylColumn:
            """
            Return a copy of the expression with the first character capitalized and the rest lowercased.
            """
            return self._col.capitalize()

        def contains(self, substr: str | StringValue) -> VinylColumn:
            """
            Return True if the expression contains the substring and False otherwise.
            """
            return self._col.contains(substr)

        def convert_base(
            self, from_base: IntegerValue, to_base: IntegerValue
        ) -> VinylColumn:
            """
            Convert the expression from one base to another.
            """
            return self._col.convert_base(from_base, to_base)

        def endswith(self, end: str | StringValue) -> VinylColumn:
            """
            Return True if the expression ends with the specified suffix and False otherwise.
            """
            return self._col.endswith(end)

        def find_in_set(self, str_list: list[str]) -> VinylColumn:
            """
            Return the position of the first occurrence of the expression in the list of strings.
            """
            return self._col.find_in_set()

        def find(
            self,
            substr: str | StringValue,
            start: int | IntegerValue | None = None,
            end: int | IntegerValue | None = None,
        ) -> VinylColumn:
            """
            Return the position of the first occurrence of substring. Search is limited to the specified start and end positions, if provided. All indexes are 0-based.
            """
            return self._col.find(substr, start, end)

        # standard library functions added

        def format(self, *args: Any, **kwargs: Any) -> VinylColumn:
            """
            Return a formatted string using the expression as a format string.

            Note that only a subset of the python format string syntax is supported.
            ```
            *Supported*
            - {0}, {1}, .. {n} for args replacements
            - {key} for kwargs replacements

            **Not Supported**
            - conversion flags (e.g. "Harold's a clever {0\!s}")
            - implicit references (e.g. "From {} to {}")
            - positional arguments / attributes (e.g. {0.weight} or {players[0]})
            ```
            """
            base: StringValue = self._col
            for i, arg in enumerate(args):
                base = base.replace(f"{{{i}}}", arg)

            for k, v in kwargs.items():
                base = base.replace(f"{{{k}}}", v)

            return base

        def to_strptime(self, format: str | StringValue) -> VinylColumn:
            """
            Parse a string into a timestamp using the specified strptime format.
            """
            return self._col.to_timestamp(format)

        def hash(
            self,
            algorithm: Literal["md5", "sha1", "sha256", "sha512"] = "sha256",
            return_type: Literal["bytes", "hex"] = "hex",
        ) -> VinylColumn:
            """
            Return the hash of the expression using the specified algorithm.
            """
            if return_type == "bytes":
                return self._col.hashbytes(algorithm)
            return self._col.hexdigest(algorithm)

        def join(self, strings: list[str | StringValue]) -> VinylColumn:
            """
            Concatenate the elements of the list using the provided separator.
            """
            return self._col.join(strings)

        def len(self, substr: str | StringValue) -> VinylColumn:
            """
            Return the number of non-overlapping occurrences of substring in the expression.
            """
            return self._col.length()

        def levenshtein(self, other: str | StringValue) -> VinylColumn:
            """
            Return the Levenshtein distance between the expression and the other string.
            """
            return self._col.levenshtein(other)

        def lower(self) -> VinylColumn:
            """
            Return a copy of the expression with all characters lowercased.
            """
            return self._col.lower()

        def ljust(
            self,
            length: int | IntegerValue,
            fillchar: str | StringValue | None = " ",
        ) -> VinylColumn:
            """
            Return the expression padded with the provided fill character to the specified length.
            """
            if fillchar is None:
                return self._col[:length]
            else:
                return self._col.lpad(length, fillchar)

        def lstrip(self) -> VinylColumn:
            """
            Return a copy of the expression with leading whitespace removed.

            Note: doesn't support removing specific characters like the standard library function.
            """
            return self._col.lstrip()

        def repeat(self, n: int | IntegerValue) -> VinylColumn:
            """
            Return the expression repeated `n` times.
            """
            return self._col.repeat(n)

        def replace(
            self, pattern: str | StringValue, replacement: str | StringValue
        ) -> VinylColumn:
            """
            Replace the matches of an exact (non-regex) pattern with a replacement string.
            """
            return self._col.replace(pattern, replacement)

        def rjust(
            self,
            length: int | IntegerValue,
            fillchar: str | StringValue | None = " ",
        ) -> VinylColumn:
            """
            Return the expression padded with the provided fill character to the specified length.
            """
            if fillchar is None:
                return self._col[-length:]
            else:
                return self._col.rpad(length, fillchar)

        def rstrip(self) -> VinylColumn:
            """
            Return a copy of the expression with trailing whitespace removed.

            Note: doesn't support removing specific characters like the standard library function.
            """
            return self._col.rstrip()

        def split(self, delimiter: str | StringValue) -> VinylColumn:
            """
            Split the expression using the specified delimiter.
            """
            return self._col.split(delimiter)

        def startswith(self, start: str | StringValue) -> VinylColumn:
            """
            Return True if the expression starts with the specified prefix and False otherwise.
            """
            return self._col.startswith(start)

        def strip(self) -> VinylColumn:
            """
            Return a copy of the expression with leading and trailing whitespace removed.
            """
            return self._col.strip()

        def reverse(self) -> VinylColumn:
            """
            Return a copy of the expression with the characters reversed.
            """
            return self._col.reverse()

        # python standard library additions
        def center(
            self, width: int | IntegerValue, fillchar: str | StringValue | None = None
        ) -> VinylColumn:
            """
            Return the expression centered in a string of length width. Padding is done using the specified fill character.
            """
            if fillchar is None:
                return self._col.substr((self._col.length() - width) // 2, width)
            adj: VinylColumn = self.ljust(width, fillchar).str.rjust(
                width, fillchar
            )  # guarantees this is long enough
            return adj._col.substr((adj._col.length() - width) // 2, width)

        def substr(
            self, start: int | IntegerValue, length: int | IntegerValue | None = None
        ) -> StringValue:
            """
            Return a substring of the expression starting at the specified index and optionally ending at the specified index.
            """
            return self._col.substr(start, length)

        def upper(self) -> VinylColumn:
            """
            Return a copy of the expression with all characters uppercased.
            """
            return self._col.upper()

    @_transform_all_methods
    class ArrayFunctions:
        _col: ArrayColumn

        def __init__(self, col: VinylColumn):
            self._col = col

        def unnest(self) -> VinylColumn:
            """
            Unnest the array into a new table.

            Note: Rows with empty arrays are dropped in the output.
            """
            return self._col.unnest()

        def join(self, sep: str) -> VinylColumn:
            """
            Concatenate the elements of the array using the provided separator.
            """
            return self._col.join(sep)

        def filter(
            self, predicate: Callable[[Value], bool] | BooleanValue
        ) -> VinylColumn:
            """
            Return a new array containing only the elements of the original array for which the predicate is true.
            """
            return self._col.filter(predicate)

        def flatten(self) -> VinylColumn:
            """
            Remove one level of nesting from the array.
            """
            return self._col.flatten()

        def index(self, value: Value) -> VinylColumn:
            """
            Return the position of the first occurrence of the value in the array.
            """
            return self._col.index(value)

        def len(self) -> VinylColumn:
            """
            Return the length of the array.
            """
            return self._col.length()

        def map(self, func: Callable[[Value], Value]) -> VinylColumn:
            """
            Apply the function to each element of the array.

            Note: also supports more complex callables like functools.partial and lambdas with closures
            """
            return self._col.map(func)

        def remove(self, value: Value) -> VinylColumn:
            """
            Return a new array with all occurrences of the value removed. Note that in the python standard library, this method only removes the first occurrence.
            """
            return self._col.remove(value)

        def repeat(self, n: int | IntegerValue) -> VinylColumn:
            """
            Return the array repeated `n` times.
            """
            return self._col.repeat(n)

        def sort(self) -> VinylColumn:
            """
            Return a new array with the elements sorted.
            """
            return self._col.sort()

        def union(self, other: ArrayColumn) -> VinylColumn:
            """
            Return a new array with the elements of both arrays, with duplicates removed.
            """
            return self._col.union(other)

        def unique(self) -> VinylColumn:
            """
            Return a new array with the duplicate elements removed.
            """
            return self._col.unique()

        def zip(self, other: ArrayValue, *others: ArrayValue) -> VinylColumn:
            """
            Return a new array with the elements of the original array and the other arrays zipped together.

            The combined map will have f1, f2, f3, etc. as the keys.
            """
            return self._col.zip(other, *others)

        # new method
        def del_(self, index: int | IntegerValue) -> VinylColumn:
            """
            Remove the element at the specified index from the array.
            """
            return self._col[:index] + self._col[index + 1 :]

        def insert(self, index: int | IntegerValue, value: Value) -> VinylColumn:
            """
            Insert the value at the specified index in the array.
            """
            return self._col[:index] + [value] + self._col[index:]

        def max(self) -> VinylColumn:
            """
            Return the maximum value of the array
            """
            return self._col.sort()[-1]

        def min(self) -> VinylColumn:
            """
            Return the minimum value of the array
            """
            return self._col.sort()[0]

    @_transform_all_methods
    class MapFunctions:
        _col: MapColumn

        def __init__(self, col: VinylColumn):
            self._col = col

        def contains(self, key: int | str | IntegerValue | StringValue) -> VinylColumn:
            """
            Return True if the map contains the specified key and False otherwise.
            """
            return self._col.contains(key)

        def get(self, key: Value, default: Value | None = None) -> VinylColumn:
            """
            Return the value of the specified key. If the key is not found, the default value is returned.
            """
            return self._col.get(key, default)

        def keys(self) -> VinylColumn:
            """
            Return the keys of the map.
            """
            return self._col.keys()

        def len(self) -> VinylColumn:
            """
            Return the length of the map.
            """
            return self._col.length()

        def values(self) -> VinylColumn:
            """
            Return the values of the map.
            """
            return self._col.values()

    @_transform_all_methods
    class StructFunctions:
        _col: StructColumn

        def __init__(self, col: VinylColumn):
            self._col = col

        @property
        def fields(self) -> VinylColumn:
            """
            Return a mapping from the field name to the field type of the struct
            """
            return self._col.fields

        @property
        def names(self) -> VinylColumn:
            """
            Return the names of the struct fields.
            """
            return self._col.names

        @property
        def types(self) -> VinylColumn:
            """
            Return the types of the struct fields.
            """
            return self._col.types

        def destructure(self) -> VinylColumn:
            """
            Destructure a StructValue into the corresponding struct fields.

            When assigned, a destruct value will be destructured and assigned to multiple columns.
            """
            return self._col.destructure()

        def lift(self) -> VinylColumn:
            """
            Project the fields of self into a table.

            This method is useful when analyzing data that has deeply nested structs or arrays of structs. lift can be chained to avoid repeating column names and table references.
            """
            return self._col.lift()

    @_transform_all_methods
    class TemporalFunctions:
        _col: TimestampValue | DateValue | IntervalValue

        def __init__(self, col: VinylColumn):
            self._col = col

        def extract(
            self,
            unit: Literal[
                "year",
                "quarter",
                "month",
                "week_of_year",
                "day",
                "day_of_year",
                "hour",
                "minute",
                "second",
                "microsecond",
                "millisecond",
            ],
        ) -> VinylColumn:
            """
            Extract the specified component from the datetime expression.
            """
            if unit == "year":
                return self._col.year()

            elif unit == "quarter":
                return self._col.quarter()

            elif unit == "month":
                return self._col.month()

            elif unit == "week_of_year":
                return self._col.week()

            elif unit == "day":
                return self._col.day()

            elif unit == "day_of_year":
                return self._col.day_of_year()

            elif unit == "hour":
                return self._col.hour()

            elif unit == "minute":
                return self._col.minute()

            elif unit == "second":
                return self._col.second()

            elif unit == "microsecond":
                return self._col.microsecond()

            elif unit == "millisecond":
                return self._col.millisecond()

            else:
                raise ValueError("Invalid unit")

        def floor(
            self,
            years: int | IntegerValue | None = None,
            quarters: int | IntegerValue | None = None,
            months: int | IntegerValue | None = None,
            weeks: int | IntegerValue | None = None,
            days: int | IntegerValue | None = None,
            hours: int | IntegerValue | None = None,
            minutes: int | IntegerValue | None = None,
            seconds: int | IntegerValue | None = None,
            milliseconds: int | IntegerValue | None = None,
            offset: IntervalValue | None = None,
        ) -> VinylColumn:
            """
            Round down the datetime expression to the specified unit. If an offset is specified, then the datetime will be rounded down to the nearest unit after the offset.

            If multiple units are specified, these will be combined together to form the unit. E.g. 1 quarter and 1 month will be transformed to 4 months.
            """
            unit_keys = ["Y", "Q", "M", "W", "D", "h", "m", "s", "ms", "us"]
            specified_units = [
                years,
                quarters,
                months,
                weeks,
                days,
                hours,
                minutes,
                seconds,
                milliseconds,
            ]
            if all(unit is None for unit in specified_units):
                raise ValueError("At least one unit must be specified")
            elif (
                specified_units.count(1) == 1
                and sum([u for u in specified_units if u is not None]) == 1
                and offset is None
            ):
                # can use truncate, which is supported by more backends
                specified_unit_key = [
                    unit_keys[i] for i, unit in enumerate(specified_units) if unit == 1
                ][0]
                return self._col.truncate(specified_unit_key)
            else:
                if not isinstance(self._col, TimestampValue) and not isinstance(
                    self._col, Deferred
                ):
                    raise ValueError(
                        f"Only simple units (e.g. 1 day, 1 week) are supported for {type(self._col)}. Please cast to a timestamp before using this method or use a simple unit instead."
                    )
                return self._col.bucket(
                    years=years,
                    quarters=quarters,
                    months=months,
                    weeks=weeks,
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    milliseconds=milliseconds,
                    offset=offset,
                )

        def epoch_seconds(self) -> VinylColumn:
            """
            Return the number of seconds since the Unix epoch.
            """
            return self._col.epoch_seconds()

        def strftime(self, format: str | StringValue) -> VinylColumn:  # type: ignore[valid-type]
            """
            Format string may depend on the backend, but we try to conform to ANSI strftime.
            """
            return self._col.strftime(format)


def _demote_arg(arg: Any) -> Value:
    if isinstance(arg, VinylColumn):
        return arg._col
    elif isinstance(arg, dict):
        return {_demote_arg(k): _demote_arg(v) for k, v in arg.items()}
    elif isinstance(arg, list):
        return [_demote_arg(v) for v in arg]
    elif isinstance(arg, tuple):
        return tuple(_demote_arg(v) for v in arg)
    elif isinstance(arg, set):
        return {_demote_arg(v) for v in arg}

    return arg


def _demote_args(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        new_args = []
        for i, arg in enumerate(args):
            new_args.append(_demote_arg(arg))
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = _demote_arg(v)

        return func(self, *new_args, **new_kwargs)

    return wrapper


def _demote_args_outside_class(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for i, arg in enumerate(args):
            new_args.append(_demote_arg(arg))
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = _demote_arg(v)

        return func(*new_args, **new_kwargs)

    return wrapper
