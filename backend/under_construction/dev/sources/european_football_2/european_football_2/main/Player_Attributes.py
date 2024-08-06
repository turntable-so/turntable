# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import european_football_2 # noqa F401 


@source(resource=european_football_2)
class PlayerAttributes:
    _table = "Player_Attributes"
    _unique_name = "european_football_2.european_football_2.main.PlayerAttributes"
    _schema = "main"
    _database = "european_football_2"
    _twin_path = "data/european_football_2/main/european_football_2.duckdb"
    _path = "data/dev_databases/european_football_2/european_football_2.sqlite"
    _row_count = 183978
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(description='''the unique id for players''', primary_key=True)
    player_fifa_api_id: t.Int64(nullable=True) = Field(description='''the id of the player fifa api''')
    player_api_id: t.Int64(nullable=True) = Field(description='''the id of the player api''', foreign_key=('Player', 'player_api_id'))
    date: t.String(nullable=True) = Field(description='''date. Additional context: e.g. 2016-02-18 00:00:00''')
    overall_rating: t.Int64(nullable=True) = Field(description='''the overall rating of the player. Additional context: commonsense reasoning: 
The rating is between 0-100 which is calculated by FIFA.
 Higher overall rating means the player has a stronger overall strength.''')
    potential: t.Int64(nullable=True) = Field(description='''potential of the player. Additional context: commonsense reasoning: 
The potential score is between 0-100 which is calculated by FIFA.
 Higher potential score means that the player has more potential''')
    preferred_foot: t.String(nullable=True) = Field(description='''the player's preferred foot when attacking. Additional context: right/ left''')
    attacking_work_rate: t.String(nullable=True) = Field(description='''the player's attacking work rate. Additional context: commonsense reasoning: 
• high: implies that the player is going to be in all of your attack moves
• medium: implies that the player will select the attack actions he will join in
• low: remain in his position while the team attacks ''')
    defensive_work_rate: t.String(nullable=True) = Field(description='''the player's defensive work rate. Additional context: commonsense reasoning: 
• high: remain in his position and defense while the team attacks 
• medium: implies that the player will select the defensive actions he will join in
• low: implies that the player is going to be in all of your attack moves instead of defensing''')
    crossing: t.Int64(nullable=True) = Field(description='''the player's crossing score . Additional context: commonsense reasoning: 
Cross is a long pass into the opponent's goal towards the header of sixth-yard teammate.
 The crossing score is between 0-100 which measures the tendency/frequency of crosses in the box.
 Higher potential score means that the player performs better in crossing actions. ''')
    finishing: t.Int64(nullable=True) = Field(description='''the player's finishing rate. Additional context: 0-100 which is calculated by FIFA''')
    heading_accuracy: t.Int64(nullable=True) = Field(description='''the player's heading accuracy. Additional context: 0-100 which is calculated by FIFA''')
    short_passing: t.Int64(nullable=True) = Field(description='''the player's short passing score. Additional context: 0-100 which is calculated by FIFA''')
    volleys: t.Int64(nullable=True) = Field(description='''the player's volley score. Additional context: 0-100 which is calculated by FIFA''')
    dribbling: t.Int64(nullable=True) = Field(description='''the player's dribbling score. Additional context: 0-100 which is calculated by FIFA''')
    curve: t.Int64(nullable=True) = Field(description='''the player's curve score. Additional context: 0-100 which is calculated by FIFA''')
    free_kick_accuracy: t.Int64(nullable=True) = Field(description='''the player's free kick accuracy. Additional context: 0-100 which is calculated by FIFA''')
    long_passing: t.Int64(nullable=True) = Field(description='''the player's long passing score. Additional context: 0-100 which is calculated by FIFA''')
    ball_control: t.Int64(nullable=True) = Field(description='''the player's ball control score. Additional context: 0-100 which is calculated by FIFA''')
    acceleration: t.Int64(nullable=True) = Field(description='''the player's acceleration score. Additional context: 0-100 which is calculated by FIFA''')
    sprint_speed: t.Int64(nullable=True) = Field(description='''the player's sprint speed
. Additional context: 0-100 which is calculated by FIFA''')
    agility: t.Int64(nullable=True) = Field(description='''the player's agility. Additional context: 0-100 which is calculated by FIFA''')
    reactions: t.Int64(nullable=True) = Field(description='''the player's reactions score. Additional context: 0-100 which is calculated by FIFA''')
    balance: t.Int64(nullable=True) = Field(description='''the player's balance score. Additional context: 0-100 which is calculated by FIFA''')
    shot_power: t.Int64(nullable=True) = Field(description='''the player's shot power. Additional context: 0-100 which is calculated by FIFA''')
    jumping: t.Int64(nullable=True) = Field(description='''the player's jumping score. Additional context: 0-100 which is calculated by FIFA''')
    stamina: t.Int64(nullable=True) = Field(description='''the player's stamina score. Additional context: 0-100 which is calculated by FIFA''')
    strength: t.Int64(nullable=True) = Field(description='''the player's strength score. Additional context: 0-100 which is calculated by FIFA''')
    long_shots: t.Int64(nullable=True) = Field(description='''the player's long shots score. Additional context: 0-100 which is calculated by FIFA''')
    aggression: t.Int64(nullable=True) = Field(description='''the player's aggression score. Additional context: 0-100 which is calculated by FIFA''')
    interceptions: t.Int64(nullable=True) = Field(description='''the player's interceptions score. Additional context: 0-100 which is calculated by FIFA''')
    positioning: t.Int64(nullable=True) = Field(description='''the player's 
positioning score
. Additional context: 0-100 which is calculated by FIFA''')
    vision: t.Int64(nullable=True) = Field(description='''the player's vision score
. Additional context: 0-100 which is calculated by FIFA''')
    penalties: t.Int64(nullable=True) = Field(description='''the player's penalties score
. Additional context: 0-100 which is calculated by FIFA''')
    marking: t.Int64(nullable=True) = Field(description='''the player's markingscore. Additional context: 0-100 which is calculated by FIFA''')
    standing_tackle: t.Int64(nullable=True) = Field(description='''the player's standing tackle score. Additional context: 0-100 which is calculated by FIFA''')
    sliding_tackle: t.Int64(nullable=True) = Field(description='''the player's sliding tackle score. Additional context: 0-100 which is calculated by FIFA''')
    gk_diving: t.Int64(nullable=True) = Field(description='''the player's goalkeep diving score. Additional context: 0-100 which is calculated by FIFA''')
    gk_handling: t.Int64(nullable=True) = Field(description='''the player's goalkeep diving score. Additional context: 0-100 which is calculated by FIFA''')
    gk_kicking: t.Int64(nullable=True) = Field(description='''the player's goalkeep kicking score. Additional context: 0-100 which is calculated by FIFA''')
    gk_positioning: t.Int64(nullable=True) = Field(description='''the player's goalkeep positioning score. Additional context: 0-100 which is calculated by FIFA''')
    gk_reflexes: t.Int64(nullable=True) = Field(description='''the player's goalkeep reflexes score. Additional context: 0-100 which is calculated by FIFA''')

