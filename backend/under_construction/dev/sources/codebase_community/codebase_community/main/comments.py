# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Comments:
    _table = "comments"
    _unique_name = "codebase_community.codebase_community.main.Comments"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 174285
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the comment Id''', primary_key=True)
    PostId: t.Int64(nullable=True) = Field(description='''the unique id of the post''')
    Score: t.Int64(nullable=True) = Field(description='''rating score. Additional context: 
The score is from 0 to 100. The score more than 60 refers that the comment is a positive comment. The score less than 60 refers that the comment is a negative comment. ''')
    Text: t.String(nullable=True) = Field(description='''the detailed content of the comment''')
    CreationDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the creation date of the comment''')
    UserId: t.Int64(nullable=True) = Field(description='''the id of the user who post the comment''')
    UserDisplayName: t.String(nullable=True) = Field(description='''user's display name''')

