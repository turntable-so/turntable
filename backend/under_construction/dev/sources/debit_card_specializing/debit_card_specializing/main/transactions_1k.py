# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import debit_card_specializing # noqa F401 


@source(resource=debit_card_specializing)
class Transactions1k:
    _table = "transactions_1k"
    _unique_name = "debit_card_specializing.debit_card_specializing.main.Transactions1k"
    _schema = "main"
    _database = "debit_card_specializing"
    _twin_path = "data/debit_card_specializing/main/debit_card_specializing.duckdb"
    _path = "data/dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    _row_count = 1000
    _col_replace = {}

    TransactionID: t.Int64(nullable=True) = Field(description='''Transaction ID''')
    Date: t.Date(nullable=True) = Field(description='''Date''')
    Time: t.String(nullable=True) = Field(description='''Time''')
    CustomerID: t.Int64(nullable=True) = Field(description='''Customer ID''')
    CardID: t.Int64(nullable=True) = Field(description='''Card ID''')
    GasStationID: t.Int64(nullable=True) = Field(description='''Gas Station ID''')
    ProductID: t.Int64(nullable=True) = Field(description='''Product ID''')
    Amount: t.Int64(nullable=True) = Field(description='''Amount''')
    Price: t.Float64(nullable=True) = Field(description='''Price. Additional context: 

total price = Amount x Price''')

