# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Laptimes:
    _table = "lapTimes"
    _unique_name = "formula_1.formula_1.main.Laptimes"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 420369
    _col_replace = {}

    raceId: t.Int64(nullable=False)
    driverId: t.Int64(nullable=False)
    lap: t.Int64(nullable=False)
    position: t.Int64(nullable=True)
    time: t.String(nullable=True)
    milliseconds: t.Int64(nullable=True)

