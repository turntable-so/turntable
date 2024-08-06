import re
from typing import Any, Literal

from sqlglot import Expression, exp, parse
from sqlglot.errors import OptimizeError, ParseError
from sqlglot.optimizer import Scope, optimize
from sqlglot.optimizer.qualify_columns import qualify_columns

TABLE_HELPER_NAME = "TURNTABLE_TABLE_HELPER_NAME"
MAX_PARSE_ATTEMPTS = 5
MAX_OPTIMIZE_ATTEMPTS = 5


def adj_parse(
    sql: str | None = None,
    dialect: str | None = None,
    attempts: int = 0,
):
    if attempts >= MAX_PARSE_ATTEMPTS:
        raise ValueError("Failed to parse sql")

    try:
        return parse(sql, dialect=dialect)[0]
    except ParseError as e:
        if str(e).startswith("Failed to parse any statement following CTE"):
            return adj_parse(sql=sql + " select 1", attempts=attempts + 1)
        if str(e).startswith("Expecting )."):
            return adj_parse(sql=sql + ")", attempts=attempts + 1)
        raise e


def adj_qualify(
    parsed: Expression,
    schema: dict[str, Any] | None = None,
    dialect: str | None = None,
    attempts: int = 0,
):
    if attempts >= MAX_OPTIMIZE_ATTEMPTS:
        raise ValueError("Failed to optimize sql")
    try:
        return optimize(
            expression=parsed, schema=schema, dialect=dialect, rules=(qualify_columns,)
        )
    except OptimizeError as e:  # noqa
        # remove everything but the ctes
        unknown_table_str = "Unknown table: "
        if str(e).startswith(unknown_table_str):
            table_name = str(e).replace(unknown_table_str, "").strip()
            sql = parsed.sql()
            sql += "from " + table_name
            new_parsed = adj_parse(sql=sql, dialect=dialect)
            return adj_qualify(
                parsed=new_parsed, schema=schema, dialect=dialect, attempts=attempts + 1
            )

        new_parsed = exp.Select(expressions=[exp.Literal(this=1)])
        new_parsed.set("with", exp.With(expressions=parsed.ctes))
        return adj_qualify(
            parsed=new_parsed, schema=schema, dialect=dialect, attempts=attempts + 1
        )


def _match_helper(before_sql, after_sql, pattern):
    match = re.search(pattern, after_sql, re.IGNORECASE)
    if match:
        before_sql = before_sql + " " + match.group(0)
        after_sql = after_sql[match.end() :]
    return before_sql, after_sql, bool(match)


def _sql_adjuster(
    entity_name, before_sql, after_sql, type_: Literal["table", "column"]
):
    # see if table name can be found afterwards
    pattern = r"\bfrom\s+[`a-zA-Z0-9_.-]+"
    before_sql, after_sql, match = _match_helper(before_sql, after_sql, pattern)
    if not match and type_ == "column":
        return before_sql + f" from {entity_name}"

    pattern = r"\bas\s+[`a-zA-Z0-9_.-]+"
    before_sql, after_sql, match = _match_helper(before_sql, after_sql, pattern)

    pattern = r"\bjoin\b\s+[`a-zA-Z0-9_.-]+"
    before_sql, after_sql, match = _match_helper(before_sql, after_sql, pattern)

    pattern = r"\bas\s+[`a-zA-Z0-9_.-]+"
    before_sql, after_sql, match = _match_helper(before_sql, after_sql, pattern)

    return before_sql


def _table_complete_helper(before_sql: str, after_sql: str, dialect: str | None = None):
    before_sql += " " + TABLE_HELPER_NAME
    sql = _sql_adjuster(TABLE_HELPER_NAME, before_sql, after_sql, "table")
    parsed = adj_parse(sql=sql, dialect=dialect)
    for x in parsed.find_all(exp.Table):
        if x.alias_or_name == TABLE_HELPER_NAME:
            scope = Scope(x.parent_select)
            return [x.alias_or_name for x in scope.ctes]
    raise ValueError("Failed to find table")


def table_complete(before_sql: str, after_sql: str, dialect: str | None = None):
    try:
        return _table_complete_helper(
            before_sql=before_sql, after_sql=after_sql, dialect=dialect
        )
    except Exception:
        # try without the after_sql
        return _table_complete_helper(
            before_sql=before_sql, after_sql="", dialect=dialect
        )


def _column_complete_helper(
    before_sql: str,
    after_sql: str,
    schema: dict[str, Any],
    dialect: str | None = None,
    attempts: int = 0,
):
    # Get the entity name by looking at the last word in the sql, and then taking the second to last element in the period separated string. SQLglot aliases the full table name to conform to this standard (e.g. `analytics-dev-372514.analytics.agg` as `agg`)
    entity_name = before_sql.split(" ")[-1].split(".")[-2]

    # see if table name can be found afterwards
    before_sql += "*"
    sql = _sql_adjuster(entity_name, before_sql, after_sql, "column")
    parsed = adj_parse(sql=sql, dialect=dialect)
    qualified = adj_qualify(parsed=parsed, schema=schema, dialect=dialect)
    for x in qualified.find_all(exp.Table, exp.CTE):
        # this runs bfs search, so should find innermost options first, but there's some risk here if ctes in subqueries have identical names to ctes in parent
        if x.alias_or_name == entity_name and isinstance(x, exp.Table):
            return sorted(x.parent_select.named_selects)
        if x.alias_or_name == entity_name and isinstance(x, exp.CTE):
            return sorted(x.this.named_selects)

    raise ValueError("Failed to find table")


def column_complete(
    before_sql: str,
    after_sql: str,
    schema: dict[str, Any],
    dialect: str | None = None,
    attempts: int = 0,
):
    try:
        return _column_complete_helper(
            before_sql=before_sql, after_sql=after_sql, schema=schema, dialect=dialect
        )
    except Exception:
        # try without the after_sql
        return _column_complete_helper(
            before_sql=before_sql, after_sql="", schema=schema, dialect=dialect
        )
