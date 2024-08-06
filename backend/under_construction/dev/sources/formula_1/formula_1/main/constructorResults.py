# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Constructorresults:
    _table = "constructorResults"
    _unique_name = "formula_1.formula_1.main.Constructorresults"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 11082
    _col_replace = {}

    constructorResultsId: t.Int64(nullable=True) = Field(description='''constructor Results Id''')
    raceId: t.Int64(nullable=False) = Field(description='''race id''')
    constructorId: t.Int64(nullable=False) = Field(description='''constructor id''')
    points: t.Float64(nullable=True) = Field(description='''points''')
    status: t.String(nullable=True) = Field(description='''status''')

