import networkx as nx
from datahub.metadata.urns import DatasetUrn
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
    assets: QuerySet[Asset] | list[Asset]
    asset_links: list[AssetLink]
    columns: QuerySet[Column] | list[Column]
    column_links: list[ColumnLink]

    @classmethod
    def get_values_serializable(cls, values):
        return [make_values_serializable(model_to_dict(v)) for v in values]

    def to_dict(self):
        return {
            "asset_id": make_values_serializable(self.asset_id),
            "assets": convert_to_dict(self.assets)
            if isinstance(self.assets, QuerySet)
            else self.get_values_serializable(self.assets),
            "asset_links": self.get_values_serializable(self.asset_links),
            "column_links": self.get_values_serializable(self.column_links),
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
        return self.get_lineage_object(
            asset_id, assets_to_filter, workspace_id, lineage_type
        )

    @classmethod
    def get_lineage_object(
        cls,
        asset_id: str,
        assets_to_filter: list[str],
        workspace_id: str,
        lineage_type: ColumnLink.LineageType,
    ):
        assets = Asset.objects.filter(
            id__in=assets_to_filter, workspace_id=workspace_id
        )
        asset_links = AssetLink.objects.filter(
            source_id__in=assets_to_filter,
            target_id__in=assets_to_filter,
            workspace_id=workspace_id,
        )
        columns = Column.objects.filter(
            asset_id__in=assets_to_filter, workspace_id=workspace_id
        )
        columns_ids = columns.values_list("id", flat=True)
        column_links = ColumnLink.objects.filter(
            source_id__in=columns_ids,
            target_id__in=columns_ids,
            workspace_id=workspace_id,
        ).filter(Q(lineage_type=lineage_type) | Q(lineage_type=None))

        return Lineage(
            asset_id=asset_id,
            assets=assets,
            asset_links=asset_links,
            columns=columns,
            column_links=column_links,
        )

    @classmethod
    def get_prod_names(cls, lineage: Lineage, dev_schema: str, prod_schema: str):
        asset_id_map = {}
        for asset in lineage.assets:
            dataset_urn = DatasetUrn.from_string(asset.id)
            name = dataset_urn.name
            platform = dataset_urn.platform
            name = name.replace(f".{dev_schema}_", f".{prod_schema}_").replace(
                f".{dev_schema}.", f".{prod_schema}."
            )
            adj_urn = f"urn:li:dataset:({platform},{name},PROD)"
            asset_id_map[asset.id] = adj_urn
        column_id_map = {}
        for column in lineage.columns:
            column_id_map[column.id] = column.id.replace(
                column.asset_id, asset_id_map[column.asset_id]
            )

        return asset_id_map, column_id_map

    @classmethod
    def replace_names(
        cls,
        lineage: Lineage,
        asset_id_map: dict[str, str],
        column_id_map: dict[str, str],
        inverse: bool = False,
    ):
        if inverse:
            asset_id_map = {v: k for k, v in asset_id_map.items()}
            column_id_map = {v: k for k, v in column_id_map.items()}

        def replace_id(id_: str, id_map: dict[str, str]) -> str:
            return id_map.get(id_, id_)

        for asset in lineage.assets:
            asset.id = replace_id(asset.id, asset_id_map)
        for asset_link in lineage.asset_links:
            asset_link.source_id = replace_id(asset_link.source_id, asset_id_map)
            asset_link.target_id = replace_id(asset_link.target_id, asset_id_map)
        for column in lineage.columns:
            column.id = replace_id(column.id, column_id_map)
            column.asset_id = replace_id(column.asset_id, asset_id_map)
        for column_link in lineage.column_links:
            column_link.source_id = replace_id(column_link.source_id, column_id_map)
            column_link.target_id = replace_id(column_link.target_id, column_id_map)

        return lineage

    def enrich_lineage_with_e2e(
        cls,
        dbt_lineage: Lineage,
        asset_graph: nx.DiGraph,
        root_asset: Asset,
        dev_schema: str,
        prod_schema: str,
        lineage_type: ColumnLink.LineageType = ColumnLink.LineageType.ALL,
        depth: int = 1,
    ):
        asset_id_map, column_id_map = LineageService.get_prod_names(
            dbt_lineage, dev_schema, prod_schema
        )

        dbt_lineage = LineageService.replace_names(
            dbt_lineage, asset_id_map, column_id_map
        )
        asset_graph = nx.relabel_nodes(asset_graph, asset_id_map, copy=False)

        asset_depth_dict = {}

        # get e2e lineage
        layers = nx.bfs_layers(asset_graph, [root_asset.id])
        for i in range(depth):
            asset_depth_dict[i] = next(layers)

        BI_successors = AssetLink.dynamic_successors(
            workspace_id=root_asset.workspace_id,
            asset_depth_dict=asset_depth_dict,
            max_depth=depth,
            exclude_resource_ids=[root_asset.resource_id],
        )

        e2e_lineage = LineageService.get_lineage_object(
            asset_id=root_asset.id,
            assets_to_filter=BI_successors,
            workspace_id=root_asset.workspace_id,
            lineage_type=lineage_type,
        )

        # rename instances to dev ids
        e2e_lineage = LineageService.replace_names(
            e2e_lineage, asset_id_map, column_id_map, inverse=True
        )

        # merge dbt and e2e lineage
        dbt_lineage.assets = dbt_lineage.assets + [
            a for a in e2e_lineage.assets if a not in dbt_lineage.assets
        ]
        dbt_lineage.columns = dbt_lineage.columns + [
            c for c in e2e_lineage.columns if c not in dbt_lineage.columns
        ]
        dbt_lineage.column_links = dbt_lineage.column_links + [
            c for c in e2e_lineage.column_links if c not in dbt_lineage.column_links
        ]

        return dbt_lineage
