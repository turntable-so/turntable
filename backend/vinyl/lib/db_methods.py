import orjson

from vinyl.lib.errors import VinylError


class ValidationOutput:
    errors: list[VinylError] | None
    bytes_processed: float | None
    cost: float | None

    def __init__(
        self,
        errors: list[VinylError] | None,
        bytes_processed: float | None,
        cost: float | None,
    ):
        self.errors = errors
        self.bytes_processed = bytes_processed
        self.cost = cost

    def to_dict(self):
        return {
            "errors": [error.to_dict() for error in self.errors]
            if self.errors
            else None,
            "bytes_processed": self.bytes_processed,
            "cost": self.cost,
        }

    def to_json(self):
        return orjson.dumps(self.to_dict())
