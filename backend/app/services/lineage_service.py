from typing import Literal

from django.core.cache import caches
from django.db.models import QuerySet
from django.forms.models import model_to_dict
from mpire import WorkerPool
from pydantic import BaseModel, ConfigDict

cache = caches["default"]

_CACHE = {}

from app.models import Asset, AssetLink, Column, ColumnLink
from app.utils.obj import convert_to_dict, make_values_serializable


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
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
        lineage_type: ColumnLink.LineageType = ColumnLink.LineageType.ALL,
    ) -> Lineage:
        # convert asset_id to string because networkx node link data does not support UUID
        workspace_id = str(self.workspace_id)
        predecessor_args = {
            "asset_id": asset_id,
            "workspace_id": workspace_id,
            "depth": predecessor_depth,
        }
        successor_args = {
            "asset_id": asset_id,
            "workspace_id": workspace_id,
            "depth": successor_depth,
        }

        def execute_query(type: Literal["predecessors", "successors"]):
            if type == "predecessors":
                return AssetLink.predecessors(**predecessor_args)
            return AssetLink.successors(**successor_args)

        with WorkerPool(n_jobs=2, start_method="threading", use_dill=True) as pool:
            predecessors, sucessors = pool.map(
                lambda x: execute_query(x),
                ["predecessors", "successors"],
            )

        assets_to_filter = list(set(predecessors + sucessors + [asset_id]))

        def execute_query2(type: Literal["assets", "asset_links", "columns"]):
            if type == "assets":
                return Asset.objects.filter(
                    id__in=assets_to_filter, workspace_id=self.workspace_id
                )
            if type == "asset_links":
                return AssetLink.objects.filter(
                    source_id__in=assets_to_filter, workspace_id=self.workspace_id
                )
            return Column.objects.filter(
                asset_id__in=assets_to_filter, workspace_id=self.workspace_id
            )

        with WorkerPool(n_jobs=3, start_method="threading") as pool:
            assets, asset_links, columns = pool.map(
                execute_query2,
                ["assets", "asset_links", "columns"],
            )
        column_links = ColumnLink.objects.filter(
            source_id__in=columns.values_list("id", flat=True),
            workspace_id=self.workspace_id,
            # lineage_type=lineage_type,
        )

        return Lineage(
            asset_id=asset_id,
            assets=assets,
            asset_links=asset_links,
            columns=columns,
            column_links=column_links,
        )
