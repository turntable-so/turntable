# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_filesystem  # noqa F401


@source(resource=local_filesystem)
class HolidaysEvents:
    _table = "holidays_events"
    _unique_name = "local_filesystem.HolidaysEvents"
    _path = "data/csvs/holidays_events.csv"
    _row_count = 350
    _col_replace = {}

    date: t.Date(nullable=True)
    type: t.String(nullable=True)
    locale: t.String(nullable=True)
    locale_name: t.String(nullable=True)
    description: t.String(nullable=True)
    transferred: t.Boolean(nullable=True)
