from vinyl.lib.project import Project

# @pytest.mark.skip(
#     reason="This test only works when vinyl is hooked up to a dbt project. Now using lineage directly from turntable-cli so not necessary."
# )
# def test_dbt_lineage():
#     project = Project.bootstrap()
#     breakpoint()
#     sqlproj = project.get_sql_project(
#         ids=["internal_project.models.dbt.base_posthog__person"], parallel=False
#     )
#     sqlproj.optimize()
#     sqlproj.get_lineage()
#     assert sqlproj.stitch_lineage() != {}


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
