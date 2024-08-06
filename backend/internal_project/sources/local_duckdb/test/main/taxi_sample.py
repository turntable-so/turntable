# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_duckdb  # noqa F401


@source(resource=local_duckdb)
class TaxiSample:
    _table = "taxi_sample"
    _unique_name = "local_duckdb.test.main.TaxiSample"
    _schema = "main"
    _database = "test"
    _twin_path = "data/test/main/local_duckdb.duckdb"
    _path = "../vinyl/tests/fixtures/test.duckdb"
    _row_count = 100000
    _col_replace = {}

    vendor_id: t.String(nullable=True)
    pickup_at: t.Timestamp(timezone=None, scale=6, nullable=True)
    dropoff_at: t.Timestamp(timezone=None, scale=6, nullable=True)
    passenger_count: t.Int8(nullable=True)
    trip_distance: t.Float32(nullable=True)
    rate_code_id: t.String(nullable=True)
    store_and_fwd_flag: t.String(nullable=True)
    pickup_location_id: t.Int32(nullable=True)
    dropoff_location_id: t.Int32(nullable=True)
    payment_type: t.String(nullable=True)
    fare_amount: t.Float32(nullable=True)
    extra: t.Float32(nullable=True)
    mta_tax: t.Float32(nullable=True)
    tip_amount: t.Float32(nullable=True)
    tolls_amount: t.Float32(nullable=True)
    improvement_surcharge: t.Float32(nullable=True)
    total_amount: t.Float32(nullable=True)
    congestion_surcharge: t.Float32(nullable=True)
