# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import card_games # noqa F401 


@source(resource=card_games)
class Rulings:
    _table = "rulings"
    _unique_name = "card_games.card_games_2.main.Rulings"
    _schema = "main"
    _database = "card_games_2"
    _twin_path = "data/card_games_2/main/card_games.duckdb"
    _path = "data/dev_databases/card_games/card_games_2.sqlite"
    _row_count = 87769
    _col_replace = {}

    id: t.Int64(nullable=False)
    date: t.Date(nullable=True)
    text: t.String(nullable=True)
    uuid: t.String(nullable=True)

