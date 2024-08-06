# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Order:
    _table = "order"
    _unique_name = "financial.financial.main.Order"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 6471
    _col_replace = {}

    order_id: t.Int64(nullable=False) = Field(description='''identifying the unique order''', primary_key=True)
    account_id: t.Int64(nullable=False) = Field(description='''id number of account''', foreign_key=('Account', 'account_id'))
    bank_to: t.String(nullable=False) = Field(description='''bank of the recipient''')
    account_to: t.Int64(nullable=False) = Field(description='''account of the recipient. Additional context: each bank has unique two-letter code''')
    amount: t.Float64(nullable=False) = Field(description='''debited amount''')
    k_symbol: t.String(nullable=False) = Field(description='''purpose of the payment. Additional context: "POJISTNE" stands for insurance payment
"SIPO" stands for household payment
"LEASING" stands for leasing
"UVER" stands for loan payment''')

