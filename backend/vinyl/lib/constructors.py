from typing import Any

from ibis import date as ibis_date
from ibis import interval as ibis_interval
from ibis import literal as ibis_literal
from ibis import map as ibis_map
from ibis import now as ibis_now
from ibis import random as ibis_random
from ibis import struct as ibis_struct
from ibis import timestamp as ibis_timestamp
from ibis.expr.datatypes import DataType
from ibis.expr.types import DateValue, NumericValue, TimestampValue

from vinyl.lib.column import (
    VinylColumn,
    _demote_args_outside_class,
    _promote_output_outside_class,
)
from vinyl.lib.utils.functions import _validate


def literal(value, type=None):
    """
    Create a scalar expression from a Python value.
    """
    return ibis_literal(value, type=type)


def random() -> NumericValue:
    """
    Generate a random float between 0 inclusive and 1 exclusive.

    Similar to random.random in the Python standard library.
    """
    return ibis_random()


def now() -> VinylColumn:
    """
    Get the current timestamp.
    """
    return ibis_now()


def date(year: int, month: int | None = None, day: int | None = None) -> DateValue:
    """
    Create a date scalar expression from year, month, and day.

    Alternatively, you can create a date directly from the python standard library datetime using datetime.date()
    """
    return ibis_date(year, month, day)


def time(
    hour: str, minute: str | None = None, second: str | None = None
) -> TimestampValue:
    """
    Create a time scalar expression from hour, minute, and second.

    Alternatively, you can create a time directly from the python standard library datetime using datetime.time().
    """
    return ibis_date(hour, minute, second)


def timestamp(
    year: str | None = None,
    month: str | None = None,
    day: str | None = None,
    hour: str | None = None,
    minute: str | None = None,
    second: str | None = None,
    timezone: str | None = None,
) -> TimestampValue:
    """
    Create a timestamp scalar expression from year, month, day, hour, minute, and second.

    Specify a timezone to create a timestamp with timezone. If no timezone is specified, the timestamp will be timezone naive.
    """
    return ibis_timestamp(year, month, day, hour, minute, second)


def interval(
    years: int | None = None,
    quarters: int | None = None,
    months: int | None = None,
    weeks: int | None = None,
    days: int | None = None,
    hours: int | None = None,
    minutes: int | None = None,
    seconds: int | None = None,
    milliseconds: int | None = None,
    microseconds: int | None = None,
) -> TimestampValue:
    """
    Create an interval scalar expression from years, months, weeks, days, hours, minutes, and seconds.
    """
    return ibis_interval(
        years=years,
        quarters=quarters,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
        microseconds=microseconds,
    )


def map(map: dict[Any, Any]):
    """
    Create a map scalar expression from a Python dictionary.
    """
    return ibis_map(map)


def struct(struct: dict[str, Any], type: str | DataType | None = None):
    """
    Create a struct scalar expression from a Python dictionary.

    Optionally, you can specify a type for the struct. Otherwise, the type will be inferred
    """
    return ibis_struct(struct)


# Adjust the function arguments to work with VinylColumn syntax and add validation
literal = _validate(_promote_output_outside_class(_demote_args_outside_class(literal)))
random = _validate(_promote_output_outside_class(_demote_args_outside_class(random)))
now = _validate(_promote_output_outside_class(_demote_args_outside_class(now)))
date = _validate(_promote_output_outside_class(_demote_args_outside_class(date)))
time = _validate(_promote_output_outside_class(_demote_args_outside_class(time)))
timestamp = _validate(
    _promote_output_outside_class(_demote_args_outside_class(timestamp))
)
interval = _validate(
    _promote_output_outside_class(_demote_args_outside_class(interval))
)
map = _validate(_promote_output_outside_class(_demote_args_outside_class(map)))
struct = _validate(_promote_output_outside_class(_demote_args_outside_class(struct)))
