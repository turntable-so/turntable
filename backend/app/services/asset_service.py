import uuid
from typing import List

from django.db.models import Prefetch, QuerySet
from django.db.models.fields.reverse_related import (
    ManyToManyRel,
    ManyToOneRel,
)
import ibis

from app.models import Asset, Column, Resource
from app.utils.queryset import get_with_queryset

PAGE_SIZE = 2500


class AssetService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def _should_exclude_asset(self):
        # TODO @ian: short term solution for capchase,
        # we'll eventually want to operationalize this if we get more exclusion requests
        return lambda x: x.exclude(
            tenant_id="org_2fpSXQmvdTGCnofnrK3JkROjlOh",
            unique_name__startswith="model.capchase.dmt_",
        )

    def get_assets(
        self, repository_id: uuid.UUID, embedding_info: bool = False
    ) -> QuerySet[Asset]:
        return self._core_query(embedding_info).filter(repository__id=repository_id)

    def get_asset(self, asset_id: uuid.UUID) -> QuerySet[Asset]:
        return get_with_queryset(self._core_query(), id=asset_id)

    def get_assets_by_ids(self, asset_ids: List[str]) -> QuerySet[Asset]:
        return self._core_query().filter(id__in=asset_ids)

    def get_assets_for_resource(self, resource_id: uuid.UUID) -> QuerySet[Asset]:
        resource = Resource.objects.get(id=resource_id)
        if resource.type == "DUCKDB":
            connection = ibis.duckdb.connect(
                resource.config["file_path"], read_only=True
            )
            assets_to_delete = Asset.objects.filter(resource=resource)
            assets_to_delete.delete()

            assets = []
            for table_id in connection.list_tables():
                assets.append(
                    Asset(
                        name=table_id,
                        type="table",
                        unique_name=f"{table_id}",
                        resource=resource,
                        read_only=True,
                    )
                )

            created_assets = Asset.objects.bulk_create(assets)

            for asset in created_assets:
                table = connection.table(asset.name)
                columns = [
                    Column(
                        name=col_id,
                        type=table[col_id].type(),
                        asset=asset,
                    )
                    for col_id in table.schema()
                ]
                Column.objects.bulk_create(columns)

            return assets

        if resource.latest_repository():
            assets = resource.latest_repository().asset_set.filter(resource=resource)
            assets = self._should_exclude_asset()(assets)
            return assets
        # WARNING: we dont support non-repository backed resources at the moment.
        # We'll want to update here once we do
        else:
            return []

    def _core_query(self, embedding_info: bool = False) -> QuerySet[Asset]:
        prefetches = [self._column_prefetch(), self._resource_prefetch()]
        fields = (
            self.field_creation_helper(
                Asset, fk_exclude=["resource", "column", "assetembedding"]
            )
            + self.field_creation_helper(Column, "column")
            + ["resource__type"]
        )
        if embedding_info:
            prefetches.append("assetembedding_set")
            fields += self.field_creation_helper(AssetEmbedding, "assetembedding")

        base = (
            Asset.objects.prefetch_related(*prefetches)
            .filter(tenant_id=self.tenant_id)
            .only(*fields)
        )
        return self._should_exclude_asset()(base)

    def _resource_prefetch(self):
        return Prefetch(
            "resource",
            queryset=Resource.objects.only("type").filter(tenant_id=self.tenant_id),
        )

    def _column_prefetch(self):
        # custom prefetch is far too slow here
        return "column_set"

    @classmethod
    def field_creation_helper(cls, model, prefix=None, fk_exclude=[]):
        return [
            f"{prefix}__{field.name}" if prefix else field.name
            for field in model._meta.get_fields()
            if not isinstance(field, (ManyToOneRel, ManyToManyRel))
            and field.name not in fk_exclude
        ]
