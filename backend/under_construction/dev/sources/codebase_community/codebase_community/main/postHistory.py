# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Posthistory:
    _table = "postHistory"
    _unique_name = "codebase_community.codebase_community.main.Posthistory"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 303155
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the post history id''', primary_key=True)
    PostHistoryTypeId: t.Int64(nullable=True) = Field(description='''the id of the post history type''')
    PostId: t.Int64(nullable=True) = Field(description='''the unique id of the post''')
    RevisionGUID: t.String(nullable=True) = Field(description='''the revision globally unique id of the post''')
    CreationDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the creation date of the post''')
    UserId: t.Int64(nullable=True) = Field(description='''the user who post the post''')
    Text: t.String(nullable=True) = Field(description='''the detailed content of the post''')
    Comment: t.String(nullable=True) = Field(description='''comments of the post''')
    UserDisplayName: t.String(nullable=True) = Field(description='''user's display name''')

