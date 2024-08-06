# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Account:
    _table = "account"
    _unique_name = "financial.financial.main.Account"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 4500
    _col_replace = {}

    account_id: t.Int64(nullable=False) = Field(description='''the id of the account''', primary_key=True)
    district_id: t.Int64(nullable=False) = Field(description='''location of branch''')
    frequency: t.String(nullable=False) = Field(description='''frequency of the acount''')
    date: t.Date(nullable=False) = Field(description='''the creation date of the account. Additional context: in the form YYMMDD''')

