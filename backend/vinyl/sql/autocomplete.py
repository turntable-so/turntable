import sqlglot as sg
import sqlglot.expressions as sge
import sqlglot.optimizer as sgo
from sqlglot.optimizer.qualify import qualify


def get_column_completion(
    sql_statement: str, table_or_cte: str, dialect: str = "duckdb"
):
    parsed = sg.parse(sql_statement, dialect=dialect)[0]
    model_ast = parsed
    if model_ast is None:
        return []

    sources = []
    for x in model_ast.find_all(sge.CTE):
        # split sources if there are unions
        sources += [(x.alias, x.this)]
        x.pop()
    for x2 in model_ast.find_all(sge.With):
        x2.pop()
    sources += [("test", model_ast)]
    adj = sg.exp.Select(
        **{
            "expressions": [sge.Star()],
            "from": sge.From(
                this=sge.Table(this=sge.Identifier(this="test", quoted=False))
            ),
            "with": sge.With(
                expressions=[
                    sge.CTE(
                        alias=sge.TableAlias(
                            this=sge.Identifier(this=source[0], quoted=False)
                        ),
                        this=source[1],
                    )
                    for source in sources
                ]
            ),
        }
    )
    optimized = sgo.optimize(expression=adj, rules=[qualify])
    return [c.alias for c in optimized.expressions]


if __name__ == "__main__":
    sql = "with x as (SELECT t.three FROM my_table as t), y as (select a.two from pear as a) select y.* from y left join x"
    # sql = "with x as (SELECT t.three FROM my_table as t) select * from x"
    out = get_column_completion(sql, "t")
