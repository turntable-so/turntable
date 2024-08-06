# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Client:
    _table = "client"
    _unique_name = "financial.financial.main.Client"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 5369
    _col_replace = {}

    client_id: t.Int64(nullable=False) = Field(description='''the unique number''', primary_key=True)
    gender: t.String(nullable=False) = Field(description='''nan. Additional context: F：female 
M：male ''')
    birth_date: t.Date(nullable=False) = Field(description='''birth date''')
    district_id: t.Int64(nullable=False) = Field(description='''location of branch''')

