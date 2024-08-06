# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Posts:
    _table = "posts"
    _unique_name = "codebase_community.codebase_community.main.Posts"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 91966
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the post id''', primary_key=True)
    PostTypeId: t.Int64(nullable=True) = Field(description='''the id of the post type''')
    AcceptedAnswerId: t.Int64(nullable=True) = Field(description='''the accepted answer id of the post ''')
    CreaionDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the creation date of the post''')
    Score: t.Int64(nullable=True) = Field(description='''the score of the post''')
    ViewCount: t.Int64(nullable=True) = Field(description='''the view count of the post. Additional context: 
Higher view count means the post has higher popularity''')
    Body: t.String(nullable=True) = Field(description='''the body of the post''')
    OwnerUserId: t.Int64(nullable=True) = Field(description='''the id of the owner user''')
    LasActivityDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the last activity date''')
    Title: t.String(nullable=True) = Field(description='''the title of the post''')
    Tags: t.String(nullable=True) = Field(description='''the tag of the post''')
    AnswerCount: t.Int64(nullable=True) = Field(description='''the total number of answers of the post''')
    CommentCount: t.Int64(nullable=True) = Field(description='''the total number of comments of the post''')
    FavoriteCount: t.Int64(nullable=True) = Field(description='''the total number of favorites of the post. Additional context: 
more favorite count refers to more valuable posts. ''')
    LastEditorUserId: t.Int64(nullable=True) = Field(description='''the id of the last editor''')
    LastEditDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the last edit date''')
    CommunityOwnedDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the community owned date''')
    ParentId: t.Int64(nullable=True) = Field(description='''the id of the parent post. Additional context: 
If the parent id is null, the post is the root post. Otherwise, the post is the child post of other post. ''')
    ClosedDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the closed date of the post. Additional context: 
if ClosedDate is null or empty, it means this post is not well-finished
if CloseDate is not null or empty, it means this post has well-finished.''')
    OwnerDisplayName: t.String(nullable=True) = Field(description='''the display name of the post owner''')
    LastEditorDisplayName: t.String(nullable=True) = Field(description='''the display name of the last editor''')

