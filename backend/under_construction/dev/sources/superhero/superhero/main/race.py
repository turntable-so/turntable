# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Race:
    _table = "race"
    _unique_name = "superhero.superhero.main.Race"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 61
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the race''', primary_key=True)
    race: t.String(nullable=True) = Field(description='''the race of the superhero. Additional context: 
In the context of superheroes, a superhero's race would refer to the particular group of people that the superhero belongs to base on these physical characteristics''')

