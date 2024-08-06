# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class Attribute:
    _table = "attribute"
    _unique_name = "superhero.superhero.main.Attribute"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 6
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''the unique identifier of the attribute''', primary_key=True)
    attribute_name: t.String(nullable=True) = Field(description='''the attribute. Additional context: 
A superhero's attribute is a characteristic or quality that defines who they are and what they are capable of. This could be a physical trait, such as superhuman strength or the ability to fly, or a personal trait, such as extraordinary intelligence or exceptional bravery. ''')

