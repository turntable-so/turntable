# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Badges:
    _table = "badges"
    _unique_name = "codebase_community.codebase_community.main.Badges"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 79851
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the badge id''', primary_key=True)
    UserId: t.Int64(nullable=True) = Field(description='''the unique id of the user''')
    Name: t.String(nullable=True) = Field(description='''the badge name the user obtained''')
    Date: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the date that the user obtained the badge''')

