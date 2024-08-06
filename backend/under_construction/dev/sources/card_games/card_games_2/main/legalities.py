# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import card_games # noqa F401 


@source(resource=card_games)
class Legalities:
    _table = "legalities"
    _unique_name = "card_games.card_games_2.main.Legalities"
    _schema = "main"
    _database = "card_games_2"
    _twin_path = "data/card_games_2/main/card_games.duckdb"
    _path = "data/dev_databases/card_games/card_games_2.sqlite"
    _row_count = 427907
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''unique id identifying this legality''', primary_key=True)
    format: t.String(nullable=True) = Field(description='''format of play. Additional context: each value refers to different rules to play''')
    status: t.String(nullable=True) = Field(description='''nan. Additional context: • legal
• banned
• restricted''')
    uuid: t.String(nullable=True) = Field(foreign_key=('Cards', 'uuid'))

