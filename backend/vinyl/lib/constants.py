from typing import Literal

_TS_COL_NAME = "ts"
_METRIC_LABEL = "metric"
_DIMENSION_LABEL = "dimension"
_SCHEMA_LABEL = "schema"


class PreviewHelper:
    _preview: Literal["full", "twin"] = "full"
