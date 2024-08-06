import pytest
from vinyl.lib.connect import DatabaseFileConnector, FileConnector


def test_local_no_args():
    with pytest.raises(TypeError):
        FileConnector(path=None)._connect()


def test_connect_with_duckdb_file():
    conn = DatabaseFileConnector(
        path="../vinyl/tests/fixtures/test.duckdb", tables=["*.*.*"]
    )._connect()

    assert "taxi_sample" in conn.list_tables(database=("test", "main"))
    assert (
        conn.table(database=("test", "main"), name="taxi_sample").count().execute()
        == 100000
    )


def test_connect_with_filepath():
    conn = FileConnector(path="../vinyl/tests/fixtures/data/iris.parquet")._connect()

    assert conn.table("iris").count().execute() == 150


def test_connect_with_dir():
    conn = FileConnector(path="../vinyl/tests/fixtures/data")._connect()
    print(conn.list_tables())
    assert set(["bitcoin", "iris"]).issubset(set(conn.list_tables()))
