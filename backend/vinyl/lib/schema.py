from ibis import Schema
from vinyl.lib.utils.graphics import _print_schema


class VinylSchema:
    _schema: Schema

    def __init__(self, schema: Schema):
        self._schema = schema

    def __str__(self):
        return self._schema.__str__().replace("ibis.Schema {", "vinyl.Schema {")

    def __repr__(self):
        return self._schema.__repr__().replace("ibis.Schema {", "vinyl.Schema {")

    def items(self):
        return self._schema.items()

    def get(self, name: str):
        return self._schema.get(name)

    @property
    def names(self) -> list[str]:
        return self._schema.names

    @property
    def types(self) -> list[str]:
        return self._schema.types

    def __rich__(self):
        return _print_schema(self._schema)

    def to_dict(self):
        return {name: str(type) for name, type in self._schema.items()}
