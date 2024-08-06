# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Votes:
    _table = "votes"
    _unique_name = "codebase_community.codebase_community.main.Votes"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 38930
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the vote id''', primary_key=True)
    PostId: t.Int64(nullable=True) = Field(description='''the id of the post that is voted''')
    VoteTypeId: t.Int64(nullable=True) = Field(description='''the id of the vote type''')
    CreationDate: t.Date(nullable=True) = Field(description='''the creation date of the vote''')
    UserId: t.Int64(nullable=True) = Field(description='''the id of the voter''')
    BountyAmount: t.Int64(nullable=True) = Field(description='''the amount of bounty''')

