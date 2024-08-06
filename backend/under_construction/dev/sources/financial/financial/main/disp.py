# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Disp:
    _table = "disp"
    _unique_name = "financial.financial.main.Disp"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 5369
    _col_replace = {}

    disp_id: t.Int64(nullable=False) = Field(description='''unique number of identifying this row of record''')
    client_id: t.Int64(nullable=False) = Field(description='''id number of client''', foreign_key=('Client', 'client_id'))
    account_id: t.Int64(nullable=False) = Field(description='''id number of account''', foreign_key=('Account', 'account_id'))
    type: t.String(nullable=False) = Field(description='''type of disposition. Additional context: "OWNER" : "USER" : "DISPONENT"

the account can only have the right to issue permanent orders or apply for loans''')

