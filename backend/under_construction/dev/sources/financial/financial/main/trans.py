# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import financial # noqa F401 


@source(resource=financial)
class Trans:
    _table = "trans"
    _unique_name = "financial.financial.main.Trans"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 1056320
    _col_replace = {}

    trans_id: t.Int64(nullable=False) = Field(description='''transaction id''')
    account_id: t.Int64(nullable=False) = Field(foreign_key=('Account', 'account_id'))
    date: t.Date(nullable=False) = Field(description='''date of transaction''')
    type: t.String(nullable=False) = Field(description='''+/- transaction. Additional context: "PRIJEM" stands for credit
"VYDAJ" stands for withdrawal''')
    operation: t.String(nullable=True) = Field(description='''mode of transaction. Additional context: "VYBER KARTOU": credit card withdrawal
"VKLAD": credit in cash
"PREVOD Z UCTU" :collection from another bank
"VYBER": withdrawal in cash
"PREVOD NA UCET": remittance to another bank''')
    amount: t.Int64(nullable=False) = Field(description='''amount of money. Additional context: Unit：USD''')
    balance: t.Int64(nullable=False) = Field(description='''balance after transaction. Additional context: Unit：USD''')
    k_symbol: t.String(nullable=True) = Field(description='''nan. Additional context: "POJISTNE": stands for insurrance payment
"SLUZBY": stands for payment for statement
"UROK": stands for interest credited
"SANKC. UROK": sanction interest if negative balance
"SIPO": stands for household
"DUCHOD": stands for old-age pension
"UVER": stands for loan payment''')
    bank: t.String(nullable=True) = Field(description='''nan. Additional context: each bank has unique two-letter code''')
    account: t.Int64(nullable=True)

