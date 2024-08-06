# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_parquet  # noqa F401


@source(resource=local_parquet)
class HousePrices:
    _table = "house_prices"
    _unique_name = "local_parquet.HousePrices"
    _path = "data/parquets/house_prices.parquet"
    _row_count = 545
    _col_replace = {}

    price: t.Int64(nullable=True)
    area: t.Int64(nullable=True)
    bedrooms: t.Int64(nullable=True)
    bathrooms: t.Int64(nullable=True)
    stories: t.Int64(nullable=True)
    mainroad: t.String(nullable=True)
    guestroom: t.String(nullable=True)
    basement: t.String(nullable=True)
    hotwaterheating: t.String(nullable=True)
    airconditioning: t.String(nullable=True)
    parking: t.Int64(nullable=True)
    prefarea: t.String(nullable=True)
    furnishingstatus: t.String(nullable=True)
