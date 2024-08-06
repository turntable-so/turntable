# type: ignore
from internal_project.resources import local_filesystem  # noqa F401
from internal_project.sources.local_filesystem.stores import Stores
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401


@source(resource=local_filesystem)
class Test:
    _table = "test"
    _unique_name = "local_filesystem.Test"
    _path = "data/csvs/test.csv"
    _row_count = 28512
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(primary_key=True)
    date: t.Date(nullable=True)
    store_nbr: t.Int64(nullable=True) = Field(foreign_key=Stores.store_nbr)
    family: t.String(nullable=True)
    onpromotion: t.Int64(nullable=True)
