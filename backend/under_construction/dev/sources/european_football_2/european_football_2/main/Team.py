# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import european_football_2 # noqa F401 


@source(resource=european_football_2)
class Team:
    _table = "Team"
    _unique_name = "european_football_2.european_football_2.main.Team"
    _schema = "main"
    _database = "european_football_2"
    _twin_path = "data/european_football_2/main/european_football_2.duckdb"
    _path = "data/dev_databases/european_football_2/european_football_2.sqlite"
    _row_count = 299
    _col_replace = {}

    id: t.Int64(nullable=True) = Field(description='''the unique id for teams''', primary_key=True)
    team_api_id: t.Int64(nullable=True) = Field(description='''the id of the team api''')
    team_fifa_api_id: t.Int64(nullable=True) = Field(description='''the id of the team fifa api''')
    team_long_name: t.String(nullable=True) = Field(description='''the team's long name''')
    team_short_name: t.String(nullable=True) = Field(description='''the team's short name''')

