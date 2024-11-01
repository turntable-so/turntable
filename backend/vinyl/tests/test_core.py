from internal_project.sources.dbt_bigquery.analytics_dev_372514.dbt_itracey.companies import (
    Companies,
)
from internal_project.sources.local_duckdb.test.main.taxi_sample import TaxiSample
from internal_project.sources.local_filesystem.holidays_events import HolidaysEvents
from vinyl import FillOptions, MetricStore, join


def test_correct_dataset():
    taxi = TaxiSample()
    query = taxi.aggregate(taxi.fare_amount.count())
    result = query.execute().iloc[0, 0]
    assert result == 100000


def test_fill(vinyl_read_only):
    taxi = TaxiSample()
    query = taxi.aggregate(
        by=[taxi.store_and_fwd_flag],
        sort=[taxi.pickup_at.dt.floor(months=1)],
        cols={
            "fare_amount": taxi.fare_amount.mean(),
            "tip_amount": taxi.tip_amount.mean(),
        },
        fill=FillOptions.next,
    )
    result = query.execute()

    assert (
        result.isnull().sum().sum() == 2
    )  # still some nulls left over since can't fill last row


def test_metric(vinyl_read_only):
    taxi = TaxiSample()
    store = MetricStore()
    store = store.metric(
        tbl=taxi,
        by=[taxi.store_and_fwd_flag],
        ts=taxi.pickup_at,
        fill=lambda x: x.mean(),
        cols={
            "fare_amount": taxi.fare_amount.mean(),
            "tip_amount": taxi.tip_amount.mean(),
        },
    )

    query = store.select(
        [
            store.ts.dt.floor(years=1),
            store.fare_amount + store.tip_amount,
            store.tip_amount,
            # _.store_and_fwd_flag,
        ],
        trailing=[None, 2],
    )
    result = query.execute()
    assert result is not None


def test_federation():
    c = Companies()
    h = HolidaysEvents()

    c = c.define({"month": c.last_seen.dt.extract("month")})
    c = c.define({"day": c.last_seen.dt.extract("day")})
    h = h.define({"month": h.date.dt.extract("month")})
    h = h.define({"day": h.date.dt.extract("day")})

    out = join(c, h, on=[("month", "day")], how="inner")

    assert out.execute().shape[0] >= 100
