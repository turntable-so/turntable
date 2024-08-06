# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from dev.resources import european_football_2  # noqa F401


@source(resource=european_football_2)
class Player:
    _table = "Player"
    _unique_name = "european_football_2.european_football_2.main.Player"
    _schema = "main"
    _database = "european_football_2"
    _twin_path = "data/european_football_2/main/european_football_2.duckdb"
    _path = "data/dev_databases/european_football_2/european_football_2.sqlite"
    _row_count = 11060
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(
        description="""the unique id for players""", primary_key=True
    )
    player_api_id: t.Int64(nullable=True) = Field(
        description="""the id of the player api"""
    )
    player_name: t.String(nullable=True) = Field(description="""player name""")
    player_fifa_api_id: t.Int64(nullable=True) = Field(
        description="""the id of the player fifa api"""
    )
    birthday: t.String(nullable=True) = Field(
        description="""the player's birthday. Additional context: e.g. 1992-02-29 00:00:00 
commonsense reasoning: 
Player A is older than player B means that A's birthday is earlier than B's"""
    )
    height: t.Float32(nullable=True) = Field(description="""the player's height""")
    weight: t.Int64(nullable=True) = Field(description="""the player's weight""")
