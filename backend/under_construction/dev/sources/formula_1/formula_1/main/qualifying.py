# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Qualifying:
    _table = "qualifying"
    _unique_name = "formula_1.formula_1.main.Qualifying"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 7397
    _col_replace = {}

    qualifyId: t.Int64(nullable=True)
    raceId: t.Int64(nullable=False)
    driverId: t.Int64(nullable=False)
    constructorId: t.Int64(nullable=False)
    number: t.Int64(nullable=False)
    position: t.Int64(nullable=True)
    q1: t.String(nullable=True)
    q2: t.String(nullable=True)
    q3: t.String(nullable=True)

