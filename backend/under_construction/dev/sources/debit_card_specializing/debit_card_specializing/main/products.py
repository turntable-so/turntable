# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import debit_card_specializing # noqa F401 


@source(resource=debit_card_specializing)
class Products:
    _table = "products"
    _unique_name = "debit_card_specializing.debit_card_specializing.main.Products"
    _schema = "main"
    _database = "debit_card_specializing"
    _twin_path = "data/debit_card_specializing/main/debit_card_specializing.duckdb"
    _path = "data/dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    _row_count = 591
    _col_replace = {}

    ProductID: t.Int64(nullable=False) = Field(description='''Product ID''')
    Description: t.String(nullable=True) = Field(description='''Description''')

