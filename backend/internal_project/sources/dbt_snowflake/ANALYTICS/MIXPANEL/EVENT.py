# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401
from ibis.common.collections import FrozenDict  # noqa F401

from internal_project.resources import dbt_snowflake  # noqa F401


@source(resource=dbt_snowflake)
class Event:
    _table = "EVENT"
    _unique_name = "internal_project.sources.dbt_snowflake.ANALYTICS.MIXPANEL.Event"
    _schema = "MIXPANEL"
    _database = "ANALYTICS"
    _twin_path = "data/ANALYTICS/MIXPANEL/dbt_snowflake.duckdb"
    _col_replace = {}

    _FIVETRAN_ID: t.String(nullable=False)
    TIME: t.Timestamp(timezone=None, scale=9, nullable=True)
    NAME: t.String(nullable=True)
    DISTINCT_ID: t.String(nullable=True)
    PROPERTIES: t.JSON(nullable=True)
    IMPORT: t.Boolean(nullable=True)
    CITY: t.String(nullable=True)
    MP_COUNTRY_CODE: t.String(nullable=True)
    MP_API_ENDPOINT: t.String(nullable=True)
    SOURCE: t.String(nullable=True)
    LIB_VERSION: t.String(nullable=True)
    LOCALE: t.String(nullable=True)
    MP_PROCESSING_TIME_MS: t.Int64(nullable=True)
    ANON_ID: t.String(nullable=True)
    REFERRER: t.String(nullable=True)
    CURRENT_URL: t.String(nullable=True)
    INSERT_ID: t.String(nullable=True)
    BROWSER: t.String(nullable=True)
    MP_API_TIMESTAMP_MS: t.Int64(nullable=True)
    BROWSER_VERSION: t.Float64(nullable=True)
    REGION: t.String(nullable=True)
    MP_LIB: t.String(nullable=True)
    _FIVETRAN_SYNCED: t.Timestamp(timezone="UTC", scale=9, nullable=True)
    IDENTIFIED_ID: t.String(nullable=True)
    USER_ID: t.String(nullable=True)
    DISTINCT_ID_BEFORE_IDENTITY: t.String(nullable=True)
    SCREEN_WIDTH: t.Int64(nullable=True)
    INITIAL_REFERRING_DOMAIN: t.String(nullable=True)
    DEVICE_ID: t.String(nullable=True)
    OS: t.String(nullable=True)
    SCREEN_HEIGHT: t.Int64(nullable=True)
    INITIAL_REFERRER: t.String(nullable=True)
    IS_RESHUFFLED: t.Boolean(nullable=True)
    REFERRING_DOMAIN: t.String(nullable=True)
    DEVICE: t.String(nullable=True)
    SEARCH_ENGINE: t.String(nullable=True)
