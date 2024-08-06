# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Postlinks:
    _table = "postLinks"
    _unique_name = "codebase_community.codebase_community.main.Postlinks"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 11102
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the post link id''', primary_key=True)
    CreationDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the creation date of the post link''')
    PostId: t.Int64(nullable=True) = Field(description='''the post id''')
    RelatedPostId: t.Int64(nullable=True) = Field(description='''the id of the related post''')
    LinkTypeId: t.Int64(nullable=True) = Field(description='''the id of the link type''')

