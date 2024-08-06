# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import card_games # noqa F401 


@source(resource=card_games)
class Cards:
    _table = "cards"
    _unique_name = "card_games.card_games_2.main.Cards"
    _schema = "main"
    _database = "card_games_2"
    _twin_path = "data/card_games_2/main/card_games.duckdb"
    _path = "data/dev_databases/card_games/card_games_2.sqlite"
    _row_count = 56822
    _col_replace = {}

    id: t.Int64(nullable=False)
    artist: t.String(nullable=True) = Field(description='''The name of the artist that illustrated the card art.''')
    asciiName: t.String(nullable=True) = Field(description='''The ASCII(opens new window) (Basic/128) code formatted card name with no special unicode characters.''')
    availability: t.String(nullable=True) = Field(description='''A list of the card's available printing types.. Additional context: "arena", "dreamcast", "mtgo", "paper", "shandalar"''')
    borderColor: t.String(nullable=True) = Field(description='''The color of the card border.. Additional context: "black", "borderless", "gold", "silver", "white"''')
    cardKingdomFoilId: t.String(nullable=True) = Field(description='''card Kingdom Foil Id. Additional context: 
cardKingdomFoilId, when paired with cardKingdomId that is not Null, is incredibly powerful. ''')
    cardKingdomId: t.String(nullable=True) = Field(description='''card Kingdom Id. Additional context: A list of all the colors in the color indicator''')
    colorIdentity: t.String(nullable=True) = Field(description='''A list of all the colors found in manaCost, colorIndicator, and text''')
    colorIndicator: t.String(nullable=True) = Field(description='''A list of all the colors in the color indicator (The symbol prefixed to a card's types).''')
    colors: t.String(nullable=True) = Field(description='''A list of all the colors in manaCost and colorIndicator. . Additional context: Some cards may not have values, such as cards with "Devoid" in its text.''')
    convertedManaCost: t.Float64(nullable=True) = Field(description='''The converted mana cost of the card. Use the manaValue property.. Additional context: if value is higher, it means that this card cost more converted mana ''')
    duelDeck: t.String(nullable=True) = Field(description='''The indicator for which duel deck the card is in.''')
    edhrecRank: t.Int64(nullable=True) = Field(description='''The card rank on EDHRec''')
    faceConvertedManaCost: t.Float64(nullable=True) = Field(description='''The converted mana cost or mana value for the face for either half or part of the card. . Additional context: if value is higher, it means that this card cost more converted mana for the face''')
    faceName: t.String(nullable=True) = Field(description='''The name on the face of the card.''')
    flavorName: t.String(nullable=True) = Field(description='''The promotional card name printed above the true card name on special cards that has no game function.. Additional context: The promotional card name printed above the true card name on special cards that has no game function.''')
    flavorText: t.String(nullable=True) = Field(description='''The italicized text found below the rules text that has no game function.. Additional context: The italicized text found below the rules text that has no game function.''')
    frameEffects: t.String(nullable=True) = Field(description='''The visual frame effects.. Additional context: "colorshifted", "companion", "compasslanddfc", "devoid", "draft", "etched", "extendedart", "fullart", "inverted", "legendary", "lesson", "miracle", "mooneldrazidfc", "nyxtouched", "originpwdfc", "showcase", "snow", "sunmoondfc", "textless", "tombstone", "waxingandwaningmoondfc"''')
    frameVersion: t.String(nullable=True) = Field(description='''The version of the card frame style.. Additional context: "1993", "1997", "2003", "2015", "future"''')
    hand: t.String(nullable=True) = Field(description='''The starting maximum hand size total modifier. . Additional context: A + or - character precedes an integer. 

positive maximum hand size: +1, +2, ....
negative maximum hand size: -1, ....
neural maximum hand size: 0....''')
    hasAlternativeDeckLimit: t.Int64(nullable=False) = Field(description='''If the card allows a value other than 4 copies in a deck.. Additional context: 0: disallow 1: allow''')
    hasContentWarning: t.Int64(nullable=False) = Field(description='''If the card marked by Wizards of the Coast (opens new window) for having sensitive content. See this official article (opens new window) for more information.. Additional context: 0: doesn't have 1: has sensitve content or Wizards of the Coast

Cards with this property may have missing or degraded properties and values. ''')
    hasFoil: t.Int64(nullable=False) = Field(description='''If the card can be found in foil. Additional context: 0: cannot be found 1: can be found''')
    hasNonFoil: t.Int64(nullable=False) = Field(description='''If the card can be found in non-foil. Additional context: 0: cannot be found 1: can be found''')
    isAlternative: t.Int64(nullable=False) = Field(description='''If the card is an alternate variation to an original printing. Additional context: 0: is not 1: is''')
    isFullArt: t.Int64(nullable=False) = Field(description='''If the card has full artwork.. Additional context: 0: doesn't have, 1: has full artwork''')
    isOnlineOnly: t.Int64(nullable=False) = Field(description='''If the card is only available in online game variations.. Additional context: 0: is not 1: is''')
    isOversized: t.Int64(nullable=False) = Field(description='''If the card is oversized.. Additional context: 0: is not 1: is''')
    isPromo: t.Int64(nullable=False) = Field(description='''If the card is a promotional printing.. Additional context: 0: is not 1: is''')
    isReprint: t.Int64(nullable=False) = Field(description='''If the card has been reprinted.. Additional context: 0: has not 1: has not been''')
    isReserved: t.Int64(nullable=False) = Field(description='''If the card is on the Magic: The Gathering Reserved List (opens new window). Additional context: If the card is on the Magic, it will appear in The Gathering Reserved List''')
    isStarter: t.Int64(nullable=False) = Field(description='''If the card is found in a starter deck such as Planeswalker/Brawl decks.. Additional context: 0: is not 1: is''')
    isStorySpotlight: t.Int64(nullable=False) = Field(description='''If the card is a Story Spotlight card.. Additional context: 0: is not 1: is''')
    isTextless: t.Int64(nullable=False) = Field(description='''If the card does not have a text box.. Additional context: 
0: has a text box;
1: doesn't have a text box;''')
    isTimeshifted: t.Int64(nullable=False) = Field(description='''If the card is time shifted. Additional context: 
If the card is "timeshifted", a feature of certain sets where a card will have a different frameVersion.''')
    keywords: t.String(nullable=True) = Field(description='''A list of keywords found on the card.''')
    layout: t.String(nullable=True) = Field(description='''The type of card layout. For a token card, this will be "token"''')
    leadershipSkills: t.String(nullable=True) = Field(description='''A list of formats the card is legal to be a commander in''')
    life: t.String(nullable=True) = Field(description='''The starting life total modifier. A plus or minus character precedes an integer.''')
    loyalty: t.String(nullable=True) = Field(description='''The starting loyalty value of the card.. Additional context: Used only on cards with "Planeswalker" in its types. empty means unkown''')
    manaCost: t.String(nullable=True) = Field(description='''The mana cost of the card wrapped in brackets for each value.. Additional context: 
manaCost is unconverted mana cost''')
    mcmId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    mcmMetaId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    mtgArenaId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    mtgjsonV4Id: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    mtgoFoilId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    mtgoId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    multiverseId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    name: t.String(nullable=True) = Field(description='''The name of the card.. Additional context: Cards with multiple faces, like "Split" and "Meld" cards are given a delimiter.''')
    number: t.String(nullable=True) = Field(description='''The number of the card''')
    originalReleaseDate: t.String(nullable=True) = Field(description='''original Release Date. Additional context: The original release date in ISO 8601(opens new window) format for a promotional card printed outside of a cycle window, such as Secret Lair Drop promotions.''')
    originalText: t.String(nullable=True) = Field(description='''original Text. Additional context: The text on the card as originally printed.''')
    originalType: t.String(nullable=True) = Field(description='''original Type. Additional context: The type of the card as originally printed. Includes any supertypes and subtypes.''')
    otherFaceIds: t.String(nullable=True) = Field(description='''other Face Ids. Additional context: A list of card UUID's to this card's counterparts, such as transformed or melded faces.''')
    power: t.String(nullable=True) = Field(description='''The power of the card.. Additional context: 
∞ means infinite power
null or * refers to unknown power''')
    printings: t.String(nullable=True) = Field(description='''A list of set printing codes the card was printed in, formatted in uppercase.''')
    promoTypes: t.String(nullable=True) = Field(description='''A list of promotional types for a card.. Additional context: "arenaleague", "boosterfun", "boxtopper", "brawldeck", "bundle", "buyabox", "convention", "datestamped", "draculaseries", "draftweekend", "duels", "event", "fnm", "gameday", "gateway", "giftbox", "gilded", "godzillaseries", "instore", "intropack", "jpwalker", "judgegift", "league", "mediainsert", "neonink", "openhouse", "planeswalkerstamped", "playerrewards", "playpromo", "premiereshop", "prerelease", "promopack", "release", "setpromo", "stamped", "textured", "themepack", "thick", "tourney", "wizardsplaynetwork"''')
    purchaseUrls: t.String(nullable=True) = Field(description='''Links that navigate to websites where the card can be purchased.''')
    rarity: t.String(nullable=True) = Field(description='''The card printing rarity.''')
    scryfallId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    scryfallIllustrationId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    scryfallOracleId: t.String(nullable=True) = Field(description='''nan. Additional context: NOT USEFUL''')
    setCode: t.String(nullable=True) = Field(description='''The set printing code that the card is from.''')
    side: t.String(nullable=True) = Field(description='''The identifier of the card side. . Additional context: Used on cards with multiple faces on the same card.

if this value is empty, then it means this card doesn't have multiple faces on the same card.''')
    subtypes: t.String(nullable=True) = Field(description='''A list of card subtypes found after em-dash.''')
    supertypes: t.String(nullable=True) = Field(description='''A list of card supertypes found before em-dash.. Additional context: 
list of all types should be the union of subtypes and supertypes''')
    tcgplayerProductId: t.String(nullable=True)
    text: t.String(nullable=True) = Field(description='''The rules text of the card.''')
    toughness: t.String(nullable=True) = Field(description='''The toughness of the card.''')
    type: t.String(nullable=True) = Field(description='''The type of the card as visible, including any supertypes and subtypes.. Additional context: "Artifact", "Card", "Conspiracy", "Creature", "Dragon", "Dungeon", "Eaturecray", "Elemental", "Elite", "Emblem", "Enchantment", "Ever", "Goblin", "Hero", "Instant", "Jaguar", "Knights", "Land", "Phenomenon", "Plane", "Planeswalker", "Scariest", "Scheme", "See", "Sorcery", "Sticker", "Summon", "Token", "Tribal", "Vanguard", "Wolf", "You’ll", "instant"''')
    types: t.String(nullable=True) = Field(description='''A list of all card types of the card, including Un‑sets and gameplay variants.''')
    uuid: t.String(nullable=False) = Field(description='''The universal unique identifier (v5) generated by MTGJSON. Each entry is unique.. Additional context: NOT USEFUL''')
    variations: t.String(nullable=True)
    watermark: t.String(nullable=True) = Field(description='''The name of the watermark on the card.''')

