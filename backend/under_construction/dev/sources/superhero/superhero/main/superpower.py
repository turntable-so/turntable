# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Superpower:
    _table = "superpower"
    _unique_name = "superhero.superhero.main.Superpower"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 167
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the superpower''', primary_key=True)
    power_name: t.String(nullable=True) = Field(description='''the superpower name''')

