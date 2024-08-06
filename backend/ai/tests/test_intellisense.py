from sqlglot import exp

from intellisense.ast.completion import column_complete, table_complete


def test_nested_column_completion():
    before_sql = "with cte as (with cte as (select z.* from z) select ab as a from cte), cte2 as (select * from cte) select cte2."
    schema = {"cte2": {"y": "int"}, "z": {"zz": "int", "ab": "int"}}
    assert column_complete(before_sql=before_sql, after_sql="", schema=schema) == [
        "a",
    ]


def test_join_column_compeletion():
    schema = {
        exp.Table(
            this=exp.Identifier(this="agg", quoted=True),
            db=exp.Identifier(this="analytics", quoted=True),
            catalog=exp.Identifier(this="analytics-dev-372514", quoted=True),
        ): {
            "agg": "string",
            "date": "string",
            "id": "string",
            "zero": "string",
            "value": "float",
        },
        exp.Table(this=exp.Identifier(this="other")): {"y": "int"},
    }
    after_sql = "from `analytics-dev-372514`.analytics.agg as a left join other as o"
    completion = column_complete(
        before_sql="select o.", after_sql=after_sql, schema=schema, dialect="bigquery"
    )
    assert completion == ["y"]

    completion = column_complete(
        before_sql="select a.", after_sql=after_sql, schema=schema, dialect="bigquery"
    )
    assert completion == ["agg", "date", "id", "value", "zero"]


def test_table_completion():
    before_sql = "with cte as (with cte3 as (select z.* from z) select ab as a from cte), cte2 as (select * from cte) select 1 from"
    after_sql = ""
    completion = table_complete(
        before_sql=before_sql, after_sql=after_sql, dialect="bigquery"
    )
    assert (
        completion == ["cte", "cte2"]
    )  # note that cte3 and z are not included because they are not at the same level as the from that we are completing
