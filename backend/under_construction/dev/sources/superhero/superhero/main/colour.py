# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Colour:
    _table = "colour"
    _unique_name = "superhero.superhero.main.Colour"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 35
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the color''', primary_key=True)
    colour: t.String(nullable=True) = Field(description='''the color of the superhero's skin/eye/hair/etc''')

