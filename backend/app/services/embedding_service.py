from functools import lru_cache

import lancedb
import orjson
from django.db.models import QuerySet

from ai.embeddings import DEFAULT_EMBEDDING_MODEL, EmbeddingModes, embed
from app.models import AssetEmbedding
from datastore.supabase_client import supabase


class EmbeddingService:
    def __init__(
        self,
        repository_id: str = None,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.repository_id = repository_id
        self.model_name = model_name
        self.db = lancedb.connect("/tmp/db")

    def search(
        self,
        query: str,
        match_count: int = 10,
        match_threshold: float = 0.0,
        mode: EmbeddingModes = EmbeddingModes.AUTOCOMPLETE,
        use_cached_vectors: bool = True,
    ):
        query_embedding = self.embed_query(query, self.model_name)
        if not use_cached_vectors:
            helper = (
                supabase.rpc(
                    f"search_{mode.value}",
                    {
                        "match_count": match_count,
                        "match_threshold": match_threshold,
                        "query_embedding": query_embedding,
                        "repository_id": self.repository_id,
                    },
                )
                .execute()
                .data
            )
            return [v["id"] for v in helper]
        else:
            table = self.cache_lance_db(mode)
            search = (
                table.search(query_embedding)
                .limit(match_count)
                .select(["asset_id"])
                .to_list()
            )
            return [v["asset_id"] for v in search]

    def _get_vectors(self) -> QuerySet[AssetEmbedding]:
        return AssetEmbedding.objects.filter(repository_id=self.repository_id).only(
            "asset_id", "search_vector", "autocomplete_vector"
        )

    @lru_cache()
    def cache_lance_db(self, mode: EmbeddingModes):
        cached = self._get_vectors()
        table = self.db.create_table(
            name=f"{self.repository_id}_{mode.value}",
            data=[
                {
                    "asset_id": v.asset_id,
                    "vector": orjson.loads(getattr(v, f"{mode.value}_vector")),
                }
                for v in cached
            ],
            mode="overwrite",
        )
        return table

    @classmethod
    def embed_query(cls, query: str, model_name: str = DEFAULT_EMBEDDING_MODEL):
        return embed(model_name, [query])[0]
