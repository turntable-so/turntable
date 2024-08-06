# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from dev.resources import debit_card_specializing  # noqa F401


@source(resource=debit_card_specializing)
class Customers:
    _table = "customers"
    _unique_name = "debit_card_specializing.debit_card_specializing.main.Customers"
    _schema = "main"
    _database = "debit_card_specializing"
    _twin_path = "data/debit_card_specializing/main/debit_card_specializing.duckdb"
    _path = "data/dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    _row_count = 32461
    _col_replace = {}

    CustomerID: t.Int64(nullable=False) = Field(
        description="""identification of the customer""", primary_key=True
    )
    Segment: t.String(nullable=True) = Field(description="""client segment""")
    Currency: t.String(nullable=True) = Field(description="""Currency""")
