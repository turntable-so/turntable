# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import debit_card_specializing # noqa F401 


@source(resource=debit_card_specializing)
class Yearmonth:
    _table = "yearmonth"
    _unique_name = "debit_card_specializing.debit_card_specializing.main.Yearmonth"
    _schema = "main"
    _database = "debit_card_specializing"
    _twin_path = "data/debit_card_specializing/main/debit_card_specializing.duckdb"
    _path = "data/dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    _row_count = 383282
    _col_replace = {}

    CustomerID: t.Int64(nullable=False) = Field(description='''Customer ID''')
    Date: t.String(nullable=False) = Field(description='''Date''')
    Consumption: t.Float64(nullable=True) = Field(description='''consumption''')

