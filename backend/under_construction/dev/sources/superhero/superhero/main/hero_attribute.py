# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class HeroAttribute:
    _table = "hero_attribute"
    _unique_name = "superhero.superhero.main.HeroAttribute"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 3738
    _col_replace = {}

    hero_id: t.Int64(nullable=True) = Field(description='''the id of the hero
Maps to superhero(id)''', foreign_key=('Superhero', 'id'))
    attribute_id: t.Int64(nullable=True) = Field(description='''the id of the attribute
Maps to attribute(id)''', foreign_key=('Attribute', 'id'))
    attribute_value: t.Int64(nullable=True) = Field(description='''the attribute value. Additional context: 
If a superhero has a higher attribute value on a particular attribute, it means that they are more skilled or powerful in that area compared to other superheroes. For example, if a superhero has a higher attribute value for strength, they may be able to lift heavier objects or deliver more powerful punches than other superheroes.''')

