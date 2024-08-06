# type: ignore
from internal_project.resources import local_filesystem  # noqa F401
from internal_project.sources.local_filesystem.stores import Stores
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401


@source(resource=local_filesystem)
class StoreNumTransactions:
    _table = "store_num_transactions"
    _unique_name = "local_filesystem.StoreNumTransactions"
    _path = "data/csvs/store_num_transactions.csv"
    _row_count = 83488
    _col_replace = {}

    date: t.Date(nullable=True)
    store_nbr: t.Int64(nullable=True) = Field(foreign_key=Stores.store_nbr)
    transactions: t.Int64(nullable=True)
