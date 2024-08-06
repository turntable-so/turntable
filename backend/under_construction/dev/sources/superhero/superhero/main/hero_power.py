# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import superhero # noqa F401 


@source(resource=superhero)
class HeroPower:
    _table = "hero_power"
    _unique_name = "superhero.superhero.main.HeroPower"
    _schema = "main"
    _database = "superhero"
    _twin_path = "data/superhero/main/superhero.duckdb"
    _path = "data/dev_databases/superhero/superhero.sqlite"
    _row_count = 5825
    _col_replace = {}

    hero_id: t.Int64(nullable=True) = Field(description='''the id of the hero
Maps to superhero(id)''', foreign_key=('Superhero', 'id'))
    power_id: t.Int64(nullable=True) = Field(description='''the id of the power
Maps to superpower(id). Additional context: 
In general, a superhero's attributes provide the foundation for their abilities and help to define who they are, while their powers are the specific abilities that they use to fight crime and protect others.''', foreign_key=('Superpower', 'id'))

