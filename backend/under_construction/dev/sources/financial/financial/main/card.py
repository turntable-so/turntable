# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Card:
    _table = "card"
    _unique_name = "financial.financial.main.Card"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 892
    _col_replace = {}

    card_id: t.Int64(nullable=False) = Field(description='''id number of credit card''')
    disp_id: t.Int64(nullable=False) = Field(description='''disposition id''')
    type: t.String(nullable=False) = Field(description='''type of credit card. Additional context: "junior": junior class of credit card; 
"classic": standard class of credit card; 
"gold": high-level credit card''')
    issued: t.Date(nullable=False) = Field(description='''the date when the credit card issued . Additional context: in the form YYMMDD''')

