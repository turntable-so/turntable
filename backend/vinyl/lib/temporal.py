from datetime import datetime
from typing import Any, Callable

import ibis
import ibis.expr.types as ir
import pytz
from ibis.common.deferred import Deferred

from vinyl.lib.column_methods import ColumnBuilder
from vinyl.lib.settings import PyProjectSettings


def _get_utc_offset(timezone_str: str) -> float:
    # Create a timezone object
    tz = pytz.timezone(timezone_str)

    # Localize a datetime object to the specified timezone
    localized_dt = tz.localize(datetime.now())

    # Get the UTC offset in minutes
    utc_offset = localized_dt.utcoffset()
    if utc_offset is not None:
        return utc_offset.total_seconds() / 60

    raise ValueError(f"Invalid timezone: {timezone_str}")


## NOTE: This is a bit hacky. Some databases don't support timestamps with timezones effectively, so we use adjusted timestamps without timezones instead.
def _set_timezone(
    tbl: Any,  # will be vinylTable but can't import here due to circular reference
    col: ir.Value | Callable[..., Any],
    to_tz: str | None = None,
    from_tz: str = "UTC",
) -> Deferred | ir.Value:
    # Check if col is a timestamp, otherwise raise an error
    vinyl_col = ColumnBuilder(tbl, col)

    if not vinyl_col._type or not vinyl_col._type.is_timestamp():
        raise TypeError("Column must be of type timestamp")

    # If no timezone is specified, check pyproject.toml
    to_tz = (
        PyProjectSettings()._get_setting("tz")
        or str(datetime.now().astimezone().tzinfo)
        or "UTC"
    )

    # Create a timezone object
    utc_offset = _get_utc_offset(to_tz)
    if from_tz != "UTC":
        utc_offset -= _get_utc_offset(from_tz)

    # Cast to timestamp without tz (a bit hacky in ibis) and add the new timezone. Note this is a bit hacky in ibis. You can't cast to an instance of dt.Timestamp of it is deferred.
    col_as_dt = (
        col.cast(datetime) + ibis.interval(minutes=utc_offset)
        if isinstance(col, ir.Value) or isinstance(col, Deferred)
        else lambda x: col(x.tbl).cast(datetime) + ibis.interval(minutes=utc_offset)
    )
    return col_as_dt
