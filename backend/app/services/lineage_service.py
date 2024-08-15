from django.core.cache import caches
from django.db.models import Q, QuerySet
from django.forms.models import model_to_dict
from pydantic import BaseModel, ConfigDict

from app.models import Asset, AssetLink, Column, ColumnLink
from app.utils.obj import convert_to_dict, make_values_serializable

cache = caches["default"]

_CACHE = {}


class Lineage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    asset_id: str
    assets: QuerySet[Asset]
    asset_links: list[AssetLink]
    columns: QuerySet[Column]
    column_links: list[ColumnLink]

    def to_dict(self):
        return {
            "asset_id": make_values_serializable(self.asset_id),
            "assets": convert_to_dict(self.assets),
            "asset_links": [
                make_values_serializable(model_to_dict(a)) for a in self.asset_links
            ],
            "column_links": [
                make_values_serializable(model_to_dict(c)) for c in self.column_links
            ],
        }


class LineageService:
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id

    def validate_json_format(json_data):
        if not isinstance(json_data, dict):
            return False
        if "nodes" not in json_data or "links" not in json_data:
            return False
        return True

    def get_lineage(
        self,
        asset_id: str,
        predecessor_depth: int = 1,
        successor_depth: int = 1,
        lineage_type: ColumnLink.LineageType = ColumnLink.LineageType.ALL,
    ) -> Lineage:
        # convert asset_id to string because networkx node link data does not support UUID
        workspace_id = str(self.workspace_id)
        relative_args = {
            "asset_id": asset_id,
            "workspace_id": workspace_id,
            "predecessor_depth": predecessor_depth,
            "successor_depth": successor_depth,
        }
        relatives = set(AssetLink.relatives(**relative_args))
        relatives.add(asset_id)
        assets_to_filter = list(relatives)
        assets = Asset.objects.filter(
            id__in=assets_to_filter, workspace_id=self.workspace_id
        )
        asset_links = AssetLink.objects.filter(
            source_id__in=assets_to_filter,
            target_id__in=assets_to_filter,
            workspace_id=self.workspace_id,
        )
        columns = Column.objects.filter(
            asset_id__in=assets_to_filter, workspace_id=self.workspace_id
        )
        columns_ids = columns.values_list("id", flat=True)
        column_links = ColumnLink.objects.filter(
            source_id__in=columns_ids,
            target_id__in=columns_ids,
            workspace_id=self.workspace_id,
        ).filter(Q(lineage_type=lineage_type) | Q(lineage_type=None))

        return Lineage(
            asset_id=asset_id,
            assets=assets,
            asset_links=asset_links,
            columns=columns,
            column_links=column_links,
        )
