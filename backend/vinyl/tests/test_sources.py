import pytest
from vinyl import join


def test_local_csv_file():
    from internal_project.sources.local_filesystem.stores import Stores

    table = Stores()

    assert table is not None
    assert table.schema() is not None

    result = table.select([table.store_nbr, table.city]).limit(10)
    assert len(result.execute()) == 10


def test_local_join():
    from internal_project.sources.local_filesystem.store_num_transactions import (
        StoreNumTransactions,
    )
    from internal_project.sources.local_filesystem.stores import Stores

    stores = Stores()
    assert len(stores.columns) == 5

    stores_txns = join(stores, StoreNumTransactions(), on=["store_nbr"])

    assert len(stores_txns.columns) == 7

    assert len(stores_txns.limit(10).execute(format="pyarrow")) == 10


def test_local_aggregate():
    from internal_project.sources.local_filesystem.store_num_transactions import (
        StoreNumTransactions,
    )
    from internal_project.sources.local_filesystem.stores import Stores

    stores = Stores()

    stores_txns = join(stores, StoreNumTransactions(), on=["store_nbr"])

    with stores_txns as st:
        st.aggregate(
            cols={"num_transactions": st.transactions.sum()}, by=[st.store_nbr, st.city]
        )
        st.sort(by=-st.num_transactions)

    result = st.execute()

    store_nbr, city, num_txns = result.iloc[0].values

    assert store_nbr == 44
    assert city == "Quito"
    assert num_txns == 7273093


def test_duckdb_table():
    from internal_project.sources.local_duckdb.test.main.taxi_sample import TaxiSample

    table = TaxiSample()

    assert table is not None
    assert table.schema() is not None
    result = table.select([table.vendor_id, table.pickup_at]).limit(10)

    assert len(result.execute()) == 10


def test_bigquery():
    from internal_project.sources.dbt_bigquery.analytics_dev_372514.dbt_itracey.companies import (
        Companies,
    )

    table = Companies()

    result = table.limit(10)
    # uses pyarrow to get around issue with pandas types
    assert len(result.execute("pyarrow")) == 10


@pytest.mark.skip(
    reason="This test is currently being skipped because it fails due to an Ibis postgres issue."
)
def test_postgres_source():
    from internal_project.sources.supabase_copilot_postgres.postgres.public.inferences import (
        Inferences,
    )

    inf = Inferences()

    assert len(inf.limit(10).execute()) == 10


def test_snowflake_source():
    from internal_project.sources.dbt_snowflake.ANALYTICS.MIXPANEL.EVENT import Event

    event = Event()

    assert len(event.limit(10).execute()) == 10


def test_local_parquet_file_source():
    from internal_project.sources.local_parquet.house_prices import HousePrices

    table = HousePrices()

    assert len(table.limit(10).execute()) == 10


def test_local_json_file_source():
    from internal_project.sources.local_json.test_json import TestJson

    table = TestJson()

    assert len(table.limit(10).execute()) == 10
