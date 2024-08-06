# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import dbt_bigquery  # noqa F401


@source(resource=dbt_bigquery)
class Companies:
    _table = "companies"
    _unique_name = "dbt_bigquery.analytics-dev-372514.dbt_itracey.Companies"
    _schema = "dbt_itracey"
    _database = "analytics-dev-372514"
    _twin_path = "data/analytics-dev-372514/dbt_itracey/dbt_bigquery.duckdb"
    _col_replace = {}

    domain: t.String(nullable=True)
    last_seen: t.Date(nullable=True)
    num_users: t.Int64(nullable=True)
