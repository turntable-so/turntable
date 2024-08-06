# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Gender:
    _table = "gender"
    _unique_name = "superhero.superhero.main.Gender"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 3
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the gender''', primary_key=True)
    gender: t.String(nullable=True) = Field(description='''the gender of the superhero''')

