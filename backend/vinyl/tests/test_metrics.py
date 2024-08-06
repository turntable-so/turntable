from vinyl.lib.project import Project
from vinyl.lib.query_engine import QueryEngine


def test_query_metric():
    project = Project.bootstrap()
    query_engine = QueryEngine(project)

    df = query_engine._metric(
        store="fare_metrics",
        grain="days=1",
        limit=100,
    ).to_pandas()

    assert len(df.columns) == 3
    assert "total_fare" in df.columns
    assert "avg_fare" in df.columns


def test_query_derive_metric():
    project = Project.bootstrap()
    query_engine = QueryEngine(project)

    df = query_engine._metric(
        store="fare_ratio",
        grain="days=1",
        limit=100,
    ).to_pandas()

    assert len(df.columns) == 4
    assert "total_fare" in df.columns
    assert "avg_fare" in df.columns
    assert "fare_ratio" in df.columns


def test_query_nested_derive_metric():
    project = Project.bootstrap()
    query_engine = QueryEngine(project)

    df = query_engine._metric(
        store="square_fare_ratio",
        grain="days=1",
        limit=100,
    ).to_pandas()

    assert len(df.columns) == 5
    assert "total_fare" in df.columns
    assert "avg_fare" in df.columns
    assert "fare_ratio" in df.columns
    assert "square_fare_ratio" in df.columns


def test_query_metric_dimension():
    project = Project.bootstrap()
    query_engine = QueryEngine(project)

    df = query_engine._metric(
        store="fare_metrics",
        grain="days=1",
        dimensions=["store_and_fwd_flag"],
        limit=100,
    ).to_pandas()

    assert len(df.columns) == 4
    assert "total_fare" in df.columns
    assert "avg_fare" in df.columns


def test_query_metric_from_join():
    project = Project.bootstrap()
    query_engine = QueryEngine(project)

    df = query_engine._metric(
        store="sales_metrics",
        grain="months=1",
        limit=100,
    ).to_pandas()

    assert len(df.columns) == 3
    assert "total_txns" in df.columns
    assert "average_txns" in df.columns
