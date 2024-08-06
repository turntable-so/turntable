# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Circuits:
    _table = "circuits"
    _unique_name = "formula_1.formula_1.main.Circuits"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 72
    _col_replace = {}

    circuitId: t.Int64(nullable=True) = Field(description='''unique identification number of the circuit ''')
    circuitRef: t.String(nullable=False) = Field(description='''circuit reference name ''')
    name: t.String(nullable=False)
    location: t.String(nullable=True)
    country: t.String(nullable=True)
    lat: t.Float64(nullable=True)
    lng: t.Float64(nullable=True)
    alt: t.Int64(nullable=True)
    url: t.String(nullable=False)

