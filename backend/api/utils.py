# system imports
from typing import Any

import orjson

# dependency imports
from celery import Celery
from kombu import serialization
from kombu.serialization import registry


def initialize_orjson_serializer(celery: Celery) -> None:
    def deserialize(data: bytes | str) -> tuple[Any, Any, Any]:
        return orjson.loads(data)

    def serialize(data: Any) -> str:
        return orjson.dumps(data).decode("utf-8")

    # register json as a content type
    for content_type in ["json", "application/json"]:
        registry.enable(content_type)
        serialization.register(
            content_type,
            serialize,
            deserialize,
            content_type,
            content_encoding="utf-8",
        )
