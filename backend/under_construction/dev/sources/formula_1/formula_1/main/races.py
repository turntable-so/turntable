# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Races:
    _table = "races"
    _unique_name = "formula_1.formula_1.main.Races"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 976
    _col_replace = {}

    raceId: t.Int64(nullable=True)
    year: t.Int64(nullable=False)
    round: t.Int64(nullable=False)
    circuitId: t.Int64(nullable=False)
    name: t.String(nullable=False)
    date: t.Date(nullable=False)
    time: t.String(nullable=True)
    url: t.String(nullable=True)

