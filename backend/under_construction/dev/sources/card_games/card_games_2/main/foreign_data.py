# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import card_games # noqa F401 


@source(resource=card_games)
class ForeignData:
    _table = "foreign_data"
    _unique_name = "card_games.card_games_2.main.ForeignData"
    _schema = "main"
    _database = "card_games_2"
    _twin_path = "data/card_games_2/main/card_games.duckdb"
    _path = "data/dev_databases/card_games/card_games_2.sqlite"
    _row_count = 229186
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''unique id number identifying this row of data''', primary_key=True)
    flavorText: t.String(nullable=True) = Field(description='''The foreign flavor text of the card.''')
    language: t.String(nullable=True) = Field(description='''The foreign language of card.''')
    multiverseid: t.Int64(nullable=True) = Field(description='''The foreign multiverse identifier of the card.''')
    name: t.String(nullable=True) = Field(description='''The foreign name of the card.''')
    text: t.String(nullable=True) = Field(description='''The foreign text ruling of the card.''')
    type: t.String(nullable=True) = Field(description='''The foreign type of the card. Includes any supertypes and subtypes.''')
    uuid: t.String(nullable=True) = Field(foreign_key=('Cards', 'uuid'))

