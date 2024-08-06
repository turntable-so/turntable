# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Tags:
    _table = "tags"
    _unique_name = "codebase_community.codebase_community.main.Tags"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 1032
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the tag id''', primary_key=True)
    TagName: t.String(nullable=True) = Field(description='''the name of the tag''')
    Count: t.Int64(nullable=True) = Field(description='''the count of posts that contain this tag. Additional context: more counts --> this tag is more popular''')
    ExcerptPostId: t.Int64(nullable=True) = Field(description='''the excerpt post id of the tag''')
    WikiPostId: t.Int64(nullable=True) = Field(description='''the wiki post id of the tag''')

