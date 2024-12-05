from app.services.lineage_service import LineageService


def test_get_asset_lineage(prepopulated_dev_db):
    asset_id = "0:urn:li:dataset:(urn:li:dataPlatform:postgres,mydb.dbt_sl_test.raw_items,PROD)"
    out = LineageService(prepopulated_dev_db[0].workspace.id).get_lineage(
        asset_id, 2, 2
    )
    assert out.asset_id == asset_id
    assert len(out.assets) > 0
    assert len(out.asset_links) > 0
    assert len(out.columns) > 0
    assert len(out.column_links) > 0
