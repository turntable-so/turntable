# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import formula_1 # noqa F401 


@source(resource=formula_1)
class Results:
    _table = "results"
    _unique_name = "formula_1.formula_1.main.Results"
    _schema = "main"
    _database = "formula_1"
    _twin_path = "data/formula_1/main/formula_1.duckdb"
    _path = "data/dev_databases/formula_1/formula_1.sqlite"
    _row_count = 23657
    _col_replace = {}

    resultId: t.Int64(nullable=True) = Field(description='''the unique identification number identifying race result ''')
    raceId: t.Int64(nullable=False) = Field(description='''the identification number identifying the race ''')
    driverId: t.Int64(nullable=False)
    constructorId: t.Int64(nullable=False)
    number: t.Int64(nullable=True)
    grid: t.Int64(nullable=False)
    position: t.Int64(nullable=True)
    positionText: t.String(nullable=False)
    positionOrder: t.Int64(nullable=False)
    points: t.Float64(nullable=False)
    laps: t.Int64(nullable=False)
    time: t.String(nullable=True)
    milliseconds: t.Int64(nullable=True)
    fastestLap: t.Int64(nullable=True)
    rank: t.Int64(nullable=True)
    fastestLapTime: t.String(nullable=True)
    fastestLapSpeed: t.String(nullable=True)
    statusId: t.Int64(nullable=False)

