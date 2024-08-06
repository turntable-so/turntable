import pytest

from internal_project.sources.dbt_bigquery.analytics_dev_372514.dbt_itracey.companies import (
    Companies,
)
from internal_project.sources.local_filesystem.holidays_events import HolidaysEvents
from internal_project.sources.local_filesystem.store_num_transactions import (
    StoreNumTransactions,
)
from internal_project.sources.local_filesystem.stores import Stores
from vinyl import VinylTable


def test_from_sql():
    t = Stores()
    t2 = StoreNumTransactions()
    x = VinylTable.from_sql(
        "select * from t left join t2 using (store_nbr)", sources={"t": t, "t2": t2}
    )
    out = x.execute()
    assert len(out.columns) == 7
    assert len(out) == 10000


def test_from_sql_federated():
    c = Companies()
    h = HolidaysEvents()

    c = c.define({"month": c.last_seen.dt.extract("month")})
    c = c.define({"day": c.last_seen.dt.extract("day")})
    h = h.define({"month": h.date.dt.extract("month")})
    h = h.define({"day": h.date.dt.extract("day")})

    with pytest.raises(ValueError) as exc_info:
        out = VinylTable.from_sql(
            """
            select
                c.company_id,
                c.company_name,
                h.date,
                h.description
            from c
            left join h
            on c.month = h.month and c.day = h.day
            """,
            sources={"c": c, "h": h},
        )
    assert str(exc_info.value) == "Multiple backends found in sources"
