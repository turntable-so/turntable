# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_json  # noqa F401


@source(resource=local_json)
class TestJson:
    _table = "test_json"
    _unique_name = "local_json.TestJson"
    _path = "data/jsons/test_json.json"
    _row_count = 10
    _col_replace = {}

    id: t.Int64(nullable=True)
    name: t.String(nullable=True)
    age: t.Int64(nullable=True)
    email: t.String(nullable=True)
    city: t.String(nullable=True)
    country: t.String(nullable=True)
    occupation: t.String(nullable=True)
    salary: t.Int64(nullable=True)
    experience_years: t.Int64(nullable=True)
    remote: t.Boolean(nullable=True)
