from vinyl.lib.project import Project


def test_amount_base():
    project = Project.bootstrap()
    table = project._get_model("amount_base")
    assert "total_amount" in table.columns
    assert len(table.execute(limit=None)) == 100000


def test_amount_by_trip_distance():
    project = Project.bootstrap()
    table = project._get_model("amount_by_trip_distance")
    assert table.columns == ["trip_distance", "total_amount"]
    assert len(table.execute(limit=None)) == 100000


def test_amount_metric_by_day():
    project = Project.bootstrap()
    table = project._get_model("amount_metric_by_day")

    assert "total_fare" in table.columns
    assert len(table.execute(limit=None)) > 0


def test_fare_ratio_by_month():
    project = Project.bootstrap()
    table = project._get_model("fare_ratio_by_month")

    assert "fare_ratio" in table.columns
    assert len(table.columns) == 4
    assert len(table.execute(limit=None)) > 0


def test_join():
    project = Project.bootstrap()
    table = project._get_model("store_txns")
    assert len(table.execute(limit=None)) == 83488
