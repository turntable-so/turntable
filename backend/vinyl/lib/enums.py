from enum import Enum


class FillOptions(Enum):
    null = "null"
    previous = "previous"
    next = "next"


class WindowType(Enum):
    rows = "rows"
    range = "range"


class AssetType(Enum):
    MODEL = "model"
    METRIC = "metric"
