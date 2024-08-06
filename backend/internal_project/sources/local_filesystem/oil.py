# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_filesystem  # noqa F401


@source(resource=local_filesystem)
class Oil:
    _table = "oil"
    _unique_name = "local_filesystem.Oil"
    _path = "data/csvs/oil.csv"
    _row_count = 1218
    _col_replace = {}

    date: t.Date(nullable=True)
    dcoilwtico: t.Float64(nullable=True)
