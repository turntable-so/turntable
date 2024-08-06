from internal_project.sources.local_duckdb.test.main.taxi_sample import TaxiSample
from internal_project.sources.local_filesystem.store_num_transactions import (
    StoreNumTransactions,
)
from internal_project.sources.local_filesystem.stores import Stores
from vinyl import M, T, metric, model
from vinyl.lib.set import join


@model(deps=TaxiSample)
def amount_base(t: T) -> T:
    t.define({"total_amount": t.fare_amount + t.tip_amount})
    return t


@model(deps=amount_base)
def amount_by_trip_distance(m: T) -> T:
    return m.select([m.trip_distance, m.total_amount])


@metric(deps=[amount_base], publish=True)
def fare_metrics(b: T) -> M:
    m = b.metric(
        cols={
            "total_fare": b.total_amount.sum(),
            "avg_fare": b.total_amount.mean(),
        },
        by=b.store_and_fwd_flag,
        ts=b.pickup_at,
        fill=lambda x: x.mean(),
    )
    return m


@model(deps=fare_metrics)
def amount_metric_by_day(m: M) -> T:
    return m.select(
        [
            m.ts.dt.floor(years=1),
            m.total_fare,
        ],
        trailing=[None, 2],
    )


@metric(deps=[fare_metrics])
def fare_ratio(m: M) -> M:
    m.derive({"fare_ratio": m.total_fare / m.avg_fare})
    return m


@metric(deps=[fare_ratio])
def square_fare_ratio(m: M) -> M:
    m.derive({"square_fare_ratio": m.fare_ratio**2})
    return m


@model(deps=[fare_ratio])
def fare_ratio_by_month(m: M) -> T:
    return m.select(
        [
            m.ts.dt.floor(months=1),
            m.store_and_fwd_flag,
            m.fare_ratio,
        ],
        trailing=[None, 2],
    )


@model(deps=[Stores, StoreNumTransactions])
def top_stores(stores: T, txns: T) -> T:
    table = join(stores, txns, on=["store_nbr"])
    table.aggregate(
        cols={"num_transactions": table.transactions.sum()},
        by=[table.store_nbr, table.city, table.state],
    )
    return table.sort(by=[-table.num_transactions])


@model(deps=[StoreNumTransactions, Stores])
def store_txns(txns, stores):
    table = join(
        txns,
        stores,
        on=[
            stores.store_nbr == txns.store_nbr,
        ],
    )
    return table


@metric(deps=[store_txns])
def sales_metrics(table: T) -> M:
    store = table.metric(
        by=[table.store_nbr, table.city, table.state],
        ts=table.date.cast("timestamp"),
        cols={
            "total_txns": table.transactions.sum(),
            "average_txns": table.transactions.mean(),
        },
    )
    return store


# @model(deps=Inferences)
# def copilot_inferences(t: T) -> T:
#     return t
