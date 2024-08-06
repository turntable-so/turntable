# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Drivers:
    _table = "drivers"
    _unique_name = "formula_1.formula_1.main.Drivers"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 840
    _col_replace = {}

    driverId: t.Int64(nullable=True)
    driverRef: t.String(nullable=False)
    number: t.Int64(nullable=True)
    code: t.String(nullable=True)
    forename: t.String(nullable=False)
    surname: t.String(nullable=False)
    dob: t.Date(nullable=True)
    nationality: t.String(nullable=True)
    url: t.String(nullable=False)

