# type: ignore
from vinyl import Field, source  # noqa F401
from vinyl import types as t  # noqa F401

from internal_project.resources import local_filesystem  # noqa F401


@source(resource=local_filesystem)
class SampleSubmission:
    _table = "sample_submission"
    _unique_name = "local_filesystem.SampleSubmission"
    _path = "data/csvs/sample_submission.csv"
    _row_count = 28512
    _col_replace = {}

    id: t.Int64(nullable=True)
    sales: t.Float64(nullable=True)
