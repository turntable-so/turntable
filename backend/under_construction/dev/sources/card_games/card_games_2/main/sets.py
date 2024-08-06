# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import card_games # noqa F401 


@source(resource=card_games)
class Sets:
    _table = "sets"
    _unique_name = "card_games.card_games_2.main.Sets"
    _schema = "main"
    _database = "card_games_2"
    _twin_path = "data/card_games_2/main/card_games.duckdb"
    _path = "data/dev_databases/card_games/card_games_2.sqlite"
    _row_count = 551
    _col_replace = {}

    id: t.Int64(nullable=False) = Field(description='''unique id identifying this set''', primary_key=True)
    baseSetSize: t.Int64(nullable=True) = Field(description='''The number of cards in the set.''')
    block: t.String(nullable=True) = Field(description='''The block name the set was in.''')
    booster: t.String(nullable=True) = Field(description='''A breakdown of possibilities and weights of cards in a booster pack.''')
    code: t.String(nullable=False) = Field(description='''The set code for the set.''')
    isFoilOnly: t.Int64(nullable=False) = Field(description='''If the set is only available in foil.''')
    isForeignOnly: t.Int64(nullable=False) = Field(description='''If the set is available only outside the United States of America.''')
    isNonFoilOnly: t.Int64(nullable=False) = Field(description='''If the set is only available in non-foil.''')
    isOnlineOnly: t.Int64(nullable=False) = Field(description='''If the set is only available in online game variations.''')
    isPartialPreview: t.Int64(nullable=False) = Field(description='''If the set is still in preview (spoiled). Preview sets do not have complete data.''')
    keyruneCode: t.String(nullable=True) = Field(description='''The matching Keyrune code for set image icons.''')
    mcmId: t.Int64(nullable=True) = Field(description='''The Magic Card Marketset identifier.''')
    mcmIdExtras: t.Int64(nullable=True) = Field(description='''The split Magic Card Market set identifier if a set is printed in two sets. This identifier represents the second set's identifier.''')
    mcmName: t.String(nullable=True)
    mtgoCode: t.String(nullable=True) = Field(description='''The set code for the set as it appears on Magic: The Gathering Online. Additional context: 
if the value is null or empty, then it doesn't appear on Magic: The Gathering Online''')
    name: t.String(nullable=True) = Field(description='''The name of the set.''')
    parentCode: t.String(nullable=True) = Field(description='''The parent set code for set variations like promotions, guild kits, etc.''')
    releaseDate: t.Date(nullable=True) = Field(description='''The release date in ISO 8601 format for the set.''')
    tcgplayerGroupId: t.Int64(nullable=True) = Field(description='''The group identifier of the set on TCGplayer''')
    totalSetSize: t.Int64(nullable=True) = Field(description='''The total number of cards in the set, including promotional and related supplemental products but excluding Alchemy modifications - however those cards are included in the set itself.''')
    type: t.String(nullable=True) = Field(description='''The expansion type of the set.. Additional context: "alchemy", "archenemy", "arsenal", "box", "commander", "core", "draft_innovation", "duel_deck", "expansion", "from_the_vault", "funny", "masterpiece", "masters", "memorabilia", "planechase", "premium_deck", "promo", "spellbook", "starter", "token", "treasure_chest", "vanguard"''')

