from enum import Enum

import numpy  # noqa
from litellm import embedding

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def embed(ai_model_name: str, to_embed: list[str]) -> list[list[float]]:
    raw = embedding(ai_model_name, to_embed)
    return [v["embedding"] for v in raw.data]


class EmbeddingModes(Enum):
    AUTOCOMPLETE = "autocomplete"
    SEARCH = "search"
