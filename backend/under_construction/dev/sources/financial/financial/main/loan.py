# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401
from dev.resources import financial  # noqa F401


@source(resource=financial)
class Loan:
    _table = "loan"
    _unique_name = "financial.financial.main.Loan"
    _schema = "main"
    _database = "financial"
    _twin_path = "data/financial/main/financial.duckdb"
    _path = "data/dev_databases/financial/financial.sqlite"
    _row_count = 682
    _col_replace = {}

    loan_id: t.Int64(nullable=False) = Field(description='''the id number identifying the loan data''', primary_key=True)
    account_id: t.Int64(nullable=False) = Field(description='''the id number identifying the account''', foreign_key=('Account', 'account_id'))
    date: t.Date(nullable=False) = Field(description='''the date when the loan is approved''')
    amount: t.Int64(nullable=False) = Field(description='''approved amount. Additional context: unit：US dollar''')
    duration: t.Int64(nullable=False) = Field(description='''loan duration. Additional context: unit：month''')
    payments: t.Float64(nullable=False) = Field(description='''monthly payments. Additional context: unit：month''')
    status: t.String(nullable=False) = Field(description='''repayment status. Additional context: 'A' stands for contract finished, no problems;
'B' stands for contract finished, loan not paid;
'C' stands for running contract, OK so far;
'D' stands for running contract, client in debt''')

