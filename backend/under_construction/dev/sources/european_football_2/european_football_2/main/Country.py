# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import european_football_2 # noqa F401 


@source(resource=european_football_2)
class Country:
    _table = "Country"
    _unique_name = "european_football_2.european_football_2.main.Country"
    _schema = "main"
    _database = "european_football_2"
    _twin_path = "data/european_football_2/main/european_football_2.duckdb"
    _path = "data/dev_databases/european_football_2/european_football_2.sqlite"
    _row_count = 11
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(description='''the unique id for countries''', primary_key=True)
    name: t.String(nullable=True) = Field(description='''country name''')

