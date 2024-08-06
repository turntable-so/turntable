# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import codebase_community # noqa F401 


@source(resource=codebase_community)
class Users:
    _table = "users"
    _unique_name = "codebase_community.codebase_community.main.Users"
    _schema = "main"
    _database = "codebase_community"
    _twin_path = "data/codebase_community/main/codebase_community.duckdb"
    _path = "data/dev_databases/codebase_community/codebase_community.sqlite"
    _row_count = 40325
    _col_replace = {}

    Id: t.Int64(nullable=False) = Field(description='''the user id''', primary_key=True)
    Reputation: t.Int64(nullable=True) = Field(description='''the user's reputation. Additional context: 
The user with higher reputation has more influence. ''')
    CreationDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the creation date of the user account''')
    DisplayName: t.String(nullable=True) = Field(description='''the user's display name''')
    LastAccessDate: t.Timestamp(timezone=None, scale=None, nullable=True) = Field(description='''the last access date of the user account''')
    WebsiteUrl: t.String(nullable=True) = Field(description='''the website url of the user account''')
    Location: t.String(nullable=True) = Field(description='''user's location''')
    AboutMe: t.String(nullable=True) = Field(description='''the self introduction of the user''')
    Views: t.Int64(nullable=True) = Field(description='''the number of views ''')
    UpVotes: t.Int64(nullable=True) = Field(description='''the number of upvotes''')
    DownVotes: t.Int64(nullable=True) = Field(description='''the number of downvotes''')
    AccountId: t.Int64(nullable=True) = Field(description='''the unique id of the account''')
    Age: t.Int64(nullable=True) = Field(description='''user's age. Additional context:  teenager: 13-18
 adult: 19-65
 elder: > 65''')
    ProfileImageUrl: t.String(nullable=True) = Field(description='''the profile image url''')

