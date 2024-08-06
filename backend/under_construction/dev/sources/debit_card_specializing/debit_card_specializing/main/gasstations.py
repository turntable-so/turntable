# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import debit_card_specializing # noqa F401 


@source(resource=debit_card_specializing)
class Gasstations:
    _table = "gasstations"
    _unique_name = "debit_card_specializing.debit_card_specializing.main.Gasstations"
    _schema = "main"
    _database = "debit_card_specializing"
    _twin_path = "data/debit_card_specializing/main/debit_card_specializing.duckdb"
    _path = "data/dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    _row_count = 5716
    _col_replace = {}

    GasStationID: t.Int64(nullable=False) = Field(description='''Gas Station ID''')
    ChainID: t.Int64(nullable=True) = Field(description='''Chain ID''')
    Country: t.String(nullable=True)
    Segment: t.String(nullable=True) = Field(description='''chain segment''')

