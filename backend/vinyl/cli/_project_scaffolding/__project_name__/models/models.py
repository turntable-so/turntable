from __project_name__.sources.local_filesystem.store_num_transactions import (
    StoreNumTransactions,
)
from __project_name__.sources.local_filesystem.stores import Stores
from vinyl import M, T, join, metric, model


@model(deps=[Stores, StoreNumTransactions])
def top_stores(stores: T, txns: T) -> T:
    j = join(stores, txns, on=["store_nbr"])
    j.aggregate(
        cols={"num_transactions": j.transactions.sum()},
        by=[j.store_nbr, j.city, j.state],
    )
    j.sort(by=-j.num_transactions)
    return j


@model(deps=[StoreNumTransactions, Stores])
def store_txns(txns: T, stores: T) -> T:
    table = join(stores, txns, on=[stores.store_nbr == txns.store_nbr])
    return table


@metric(deps=[store_txns])
def sales_metrics(table: T) -> M:
    metric_store = table.metric(
        by=[table.store_nbr, table.city, table.state],
        ts=table.date.cast("timestamp"),
        cols={
            "total_txns": table.transactions.sum(),
            "average_txns": table.transactions.mean(),
        },
    )
    return metric_store
