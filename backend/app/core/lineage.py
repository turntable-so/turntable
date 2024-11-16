from app.core.dbt import LiveDBTParser
from app.models.resources import Resource
from vinyl.lib.dbt import DBTProject, DBTTransition
from scripts.debug.pyinstrument import pyprofile


def get_lineage_helper(
    proj: DBTProject,
    before_proj: DBTProject | None,
    resource: Resource,
    filepath: str,
    predecessor_depth: int,
    successor_depth: int,
    lineage_type: str,
    defer: bool,
    asset_only: bool = False,
):
    if defer:
        transition = DBTTransition(before_project=before_proj, after_project=proj)
        transition.mount_manifest(defer=defer)
        if not asset_only:
            transition.mount_catalog(defer=defer)
    else:
        proj.mount_manifest()
        if not asset_only:
            proj.mount_catalog()

    node_id = LiveDBTParser.get_node_id_from_filepath(proj, filepath, defer)
    if not node_id:
        raise ValueError(f"Node at filepath{filepath} not found in manifest")

    dbtparser = LiveDBTParser.parse_project(
        proj=proj,
        before_proj=before_proj,
        node_id=node_id,
        resource=resource,
        predecessor_depth=predecessor_depth,
        successor_depth=successor_depth,
        defer=defer,
        asset_only=asset_only,
    )
    lineage, _ = dbtparser.get_lineage(lineage_type=lineage_type, asset_only=asset_only)
    root_asset = None
    column_lookup = {}
    for asset in lineage.assets:
        column_lookup[asset.id] = []
    for column in lineage.columns:
        column_lookup[column.asset_id].append(column)

    for asset in lineage.assets:
        if asset.id == lineage.asset_id:
            root_asset = asset

        asset.temp_columns = column_lookup[asset.id]

    if not root_asset:
        raise ValueError(f"Root asset not found for {lineage.asset_id}")

    return root_asset, lineage
