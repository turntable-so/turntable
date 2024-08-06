# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Seasons:
    _table = "seasons"
    _unique_name = "formula_1.formula_1.main.Seasons"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 68
    _col_replace = {}

    year: t.Int64(nullable=False)
    url: t.String(nullable=False)

