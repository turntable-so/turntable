from typing import Any, Callable, Union

from sqlglot import dialects, exp, maybe_parse
from sqlglot._typing import E
from sqlglot.expressions import Expression, Identifier


def _transform(ast_: Expression, transform_func: Callable[..., Any]) -> None:
    # handles typing issues associated with null expressions
    if ast_ is None:
        pass
    else:
        ast_.transform(transform_func, copy=False)


def _unquote_table_identifier(node: E) -> Union[E, Identifier]:
    if isinstance(node, exp.Identifier) and isinstance(node.parent, exp.Table):
        return exp.Identifier(this=node.name, quoted=False)
    return node


def _unquote_tables(sql: str) -> str:
    ast: Expression = maybe_parse(sql, dialect=dialects.BigQuery)
    _transform(ast, _unquote_table_identifier)
    return ast.sql(dialect=dialects.BigQuery)
