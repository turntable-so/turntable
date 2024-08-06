# type: ignore
from internal_project.resources import local_filesystem  # noqa F401
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401


@source(resource=local_filesystem)
class Stores:
    _table = "stores"
    _unique_name = "local_filesystem.Stores"
    _path = "data/csvs/stores.csv"
    _row_count = 54
    _col_replace = {}

    store_nbr: t.Int64(nullable=True) = Field(primary_key=True)
    city: t.String(nullable=True)
    state: t.String(nullable=True)
    type: t.String(nullable=True)
    cluster: t.Int64(nullable=True)
