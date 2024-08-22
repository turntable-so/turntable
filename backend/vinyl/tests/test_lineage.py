from vinyl.lib.project import Project


def test_local_lineage():
    project = Project.bootstrap()
    sqlproj = project.get_sql_project(
        ids=["internal_project.models.other.amount_metric_by_day"], parallel=False
    )
    sqlproj.optimize()
    sqlproj.get_lineage()
    stitched = sqlproj.stitch_lineage()

    assert stitched != {}
    assert stitched["table_lineage"]["links"] != []
    assert stitched["column_lineage"]["links"] != []
