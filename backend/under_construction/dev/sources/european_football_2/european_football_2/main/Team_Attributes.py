# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import european_football_2 # noqa F401 


@source(resource=european_football_2)
class TeamAttributes:
    _table = "Team_Attributes"
    _unique_name = "european_football_2.european_football_2.main.TeamAttributes"
    _schema = "main"
    _database = "european_football_2"
    _twin_path = "data/european_football_2/main/european_football_2.duckdb"
    _path = "data/dev_databases/european_football_2/european_football_2.sqlite"
    _row_count = 1458
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(description='''the unique id for teams''', primary_key=True)
    team_fifa_api_id: t.Int64(nullable=True) = Field(description='''the id of the team fifa api''')
    team_api_id: t.Int64(nullable=True) = Field(description='''the id of the team api''')
    date: t.String(nullable=True) = Field(description='''Date. Additional context: e.g. 2010-02-22 00:00:00''')
    buildUpPlaySpeed: t.Int64(nullable=True) = Field(description='''the speed in which attacks are put together . Additional context: the score which is between 1-00 to measure the team's attack speed''')
    buildUpPlaySpeedClass: t.String(nullable=True) = Field(description='''the speed class. Additional context: commonsense reasoning: 
• Slow: 1-33
• Balanced: 34-66
• Fast: 66-100''')
    buildUpPlayDribbling: t.Int64(nullable=True) = Field(description='''the tendency/ frequency of dribbling''')
    buildUpPlayDribblingClass: t.String(nullable=True) = Field(description='''the dribbling class. Additional context: commonsense reasoning: 
• Little: 1-33
• Normal: 34-66
• Lots: 66-100''')
    buildUpPlayPassing: t.Int64(nullable=True) = Field(description='''affects passing distance and support from teammates''')
    buildUpPlayPassingClass: t.String(nullable=True) = Field(description='''the passing class. Additional context: commonsense reasoning: 
• Short: 1-33
• Mixed: 34-66
• Long: 66-100''')
    buildUpPlayPositioningClass: t.String(nullable=True) = Field(description='''A team's freedom of movement in the 1st two thirds of the pitch. Additional context: Organised / Free Form''')
    chanceCreationPassing: t.Int64(nullable=True) = Field(description='''Amount of risk in pass decision and run support''')
    chanceCreationPassingClass: t.String(nullable=True) = Field(description='''the chance creation passing class. Additional context: commonsense reasoning: 
• Safe: 1-33
• Normal: 34-66
• Risky: 66-100''')
    chanceCreationCrossing: t.Int64(nullable=True) = Field(description='''The tendency / frequency of crosses into the box''')
    chanceCreationCrossingClass: t.String(nullable=True) = Field(description='''the chance creation crossing class. Additional context: commonsense reasoning: 
• Little: 1-33
• Normal: 34-66
• Lots: 66-100''')
    chanceCreationShooting: t.Int64(nullable=True) = Field(description='''The tendency / frequency of shots taken''')
    chanceCreationShootingClass: t.String(nullable=True) = Field(description='''the chance creation shooting class. Additional context: commonsense reasoning: 
• Little: 1-33
• Normal: 34-66
• Lots: 66-100''')
    chanceCreationPositioningClass: t.String(nullable=True) = Field(description='''A team’s freedom of movement in the final third of the pitch. Additional context: Organised / Free Form''')
    defencePressure: t.Int64(nullable=True) = Field(description='''Affects how high up the pitch the team will start pressuring''')
    defencePressureClass: t.String(nullable=True) = Field(description='''the defence pressure class. Additional context: commonsense reasoning: 
• Deep: 1-33
• Medium: 34-66
• High: 66-100''')
    defenceAggression: t.Int64(nullable=True) = Field(description='''Affect the team’s approach to tackling the ball possessor''')
    defenceAggressionClass: t.String(nullable=True) = Field(description='''the defence aggression class. Additional context: commonsense reasoning: 
• Contain: 1-33
• Press: 34-66
• Double: 66-100''')
    defenceTeamWidth: t.Int64(nullable=True) = Field(description='''Affects how much the team will shift to the ball side''')
    defenceTeamWidthClass: t.String(nullable=True) = Field(description='''the defence team width class. Additional context: commonsense reasoning: 
• Narrow: 1-33
• Normal: 34-66
• Wide: 66-100''')
    defenceDefenderLineClass: t.String(nullable=True) = Field(description='''Affects the shape and strategy of the defence. Additional context: Cover/ Offside Trap''')

