import os

import pytest

from app.models import (
    Asset,
    AssetContainer,
    AssetLink,
    Column,
    ColumnLink,
    ResourceType,
)
from app.models.resources import DBDetails


def require_env_vars(*required_vars):
    """
    Decorator to skip a test if the specified environment variables are not set.

    :param required_vars: Names of required environment variables
    """
    missing_vars = [var for var in required_vars if var not in os.environ]

    def decorator(func):
        return pytest.mark.skipif(
            len(missing_vars) > 0,
            reason=f"Missing required environment variables: {', '.join(missing_vars)}",
        )(func)

    return decorator


def assert_ingest_output(resources):
    ## all tables have records
    assert Asset.objects.count() > 0
    assert AssetContainer.objects.count() > 0
    assert AssetLink.objects.count() > 0
    assert Column.objects.count() > 0
    assert ColumnLink.objects.count() > 0

    ## all assets have types
    for asset in Asset.objects.all():
        assert asset.type is not None, asset.__dict__

    ## all resources represented in assets
    for resource in resources:
        assert resource.asset_set.count() > 0

    ## at least one asset link across resources if multiple resources used
    if len(resources) > 1:
        links_across_resources = [
            v.id
            for v in AssetLink.objects.all()
            if v.source.resource.id != v.target.resource.id
        ]
        assert len(links_across_resources) > 0

    ## all connected db assets have a column link
    db_assets = Asset.objects.filter(resource__type=ResourceType.DB).values_list(
        "id", flat=True
    )
    db_assets_with_asset_links = set()
    for al in AssetLink.objects.all():
        for id in [al.source.id, al.target.id]:
            if id in db_assets:
                db_assets_with_asset_links.add(id)
    db_assets_with_column_links = set()
    for cl in ColumnLink.objects.all():
        for id in [cl.source.asset.id, cl.target.asset.id]:
            if id in db_assets:
                db_assets_with_column_links.add(id)
    assert db_assets_with_asset_links == db_assets_with_column_links

    ## check at least one db asset has a tag/descriptoin
    if any([isinstance(r.details, DBDetails) for r in resources]):
        assert Asset.objects.filter(tags__isnull=False).count() > 0
        assert Asset.objects.filter(description__isnull=False).count() > 0

    ## all assets have a name
    assert Asset.objects.filter(name__isnull=True).count() == 0

    ## all instances have workspace_ids
    assert Asset.objects.filter(workspace_id=None).count() == 0
    assert AssetLink.objects.filter(workspace_id=None).count() == 0
    assert Column.objects.filter(workspace_id=None).count() == 0
    assert ColumnLink.objects.filter(workspace_id=None).count() == 0

    ## at least one asset has a container
    assert Asset.objects.filter(containermembership__isnull=False).count() > 0
