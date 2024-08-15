import re
import typing as t
from functools import lru_cache
from typing import Any, Callable, Sequence

import ibis.expr.datatypes as dt
import ibis.expr.schema as sch
import networkx as nx
import sqlglot.expressions as sge
from datahub.metadata.urns import DatasetUrn
from sqlglot import Expression, exp
from sqlglot._typing import E
from sqlglot.dialects.dialect import Dialect
from sqlglot.errors import OptimizeError
from sqlglot.optimizer import build_scope, optimize, traverse_scope
from sqlglot.optimizer.annotate_types import annotate_types
from sqlglot.optimizer.canonicalize import canonicalize
from sqlglot.optimizer.eliminate_ctes import eliminate_ctes
from sqlglot.optimizer.eliminate_joins import eliminate_joins
from sqlglot.optimizer.eliminate_subqueries import eliminate_subqueries
from sqlglot.optimizer.normalize import normalize
from sqlglot.optimizer.optimize_joins import optimize_joins
from sqlglot.optimizer.pushdown_predicates import pushdown_predicates
from sqlglot.optimizer.pushdown_projections import pushdown_projections
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.qualify_columns import quote_identifiers
from sqlglot.optimizer.simplify import simplify
from sqlglot.optimizer.unnest_subqueries import unnest_subqueries

from vinyl.lib.errors import VinylError, VinylErrorType
from vinyl.lib.schema import VinylSchema
from vinyl.lib.table import VinylTable
from vinyl.lib.utils.graph import DAG
from vinyl.lib.utils.text import _generate_random_ascii_string


class Catalog(dict[str, sch.Schema]):
    """A catalog of tables and their schemas."""

    typemap = {
        dt.Int8: sge.DataType.Type.TINYINT,
        dt.Int16: sge.DataType.Type.SMALLINT,
        dt.Int32: sge.DataType.Type.INT,
        dt.Int64: sge.DataType.Type.BIGINT,
        dt.Float16: sge.DataType.Type.FLOAT,  # no halffloat
        dt.Float32: sge.DataType.Type.FLOAT,
        dt.Float64: sge.DataType.Type.DOUBLE,
        dt.Decimal: sge.DataType.Type.DECIMAL,
        dt.Boolean: sge.DataType.Type.BOOLEAN,
        dt.JSON: sge.DataType.Type.JSON,
        dt.Interval: sge.DataType.Type.INTERVAL,
        dt.Timestamp: sge.DataType.Type.TIMESTAMP,
        dt.Date: sge.DataType.Type.DATE,
        dt.Binary: sge.DataType.Type.BINARY,
        dt.String: sge.DataType.Type.TEXT,
        dt.Array: sge.DataType.Type.ARRAY,
        dt.Map: sge.DataType.Type.MAP,
        dt.UUID: sge.DataType.Type.UUID,
        dt.Struct: sge.DataType.Type.STRUCT,
    }

    @classmethod
    def to_sqlglot_dtype(cls, dtype: dt.DataType) -> str:
        if dtype.is_geospatial():
            return dtype.geotype
        else:
            default = dtype.__class__.__name__.lower()
            return cls.typemap.get(type(dtype), default)

    @classmethod
    def to_sqlglot_schema(cls, schema: sch.Schema) -> dict[str, str]:
        return {name: cls.to_sqlglot_dtype(dtype) for name, dtype in schema.items()}


RULES = (
    # qualify,
    pushdown_projections,
    normalize,
    unnest_subqueries,
    pushdown_predicates,
    optimize_joins,
    eliminate_subqueries,
    eliminate_joins,
    eliminate_ctes,
    quote_identifiers,
    annotate_types,
    canonicalize,
    simplify,
)


def get_adj_node_name(n):
    if isinstance(n, VinylTable):
        # is source
        return n.get_name()
    elif hasattr(n, "_unique_name"):
        return n._unique_name
    elif hasattr(n, "_module"):
        return f"{n._module}.{n.__name__}"
    else:
        raise ValueError(f"Node {n} not recognized")


def get_parents(tpl):
    if tpl[-1].parent is None:
        return tpl
    else:
        tpl += (tpl[-1].parent,)
    return get_parents(tpl)


def get_lowest_cte(tpl):
    parents = list(get_parents(tpl))
    options = [i for i in parents if isinstance(i, sge.CTE)]
    if options == []:
        return None
    return options[0].alias


def get_sqlglot_schema(
    vinylschema: dict[str, VinylSchema],
    k_transform: Callable[[str], str] = lambda x: x,
) -> dict[str, dict[str, str]]:
    adj_schema = {}
    for k, v in vinylschema.items():
        adj_schema[k_transform(k)] = Catalog.to_sqlglot_schema(v)
    return adj_schema


def validate_qualify_columns_errors(expression: E) -> list[Exception]:
    unqualified_columns = []
    errors: list[Exception] = []
    for scope in traverse_scope(expression):
        if isinstance(scope.expression, exp.Select):
            unqualified_columns.extend(scope.unqualified_columns)
            if (
                scope.external_columns
                and not scope.is_correlated_subquery
                and not scope.pivots
            ):
                for col in scope.external_columns:
                    cte = get_lowest_cte((col,))
                    errors += [
                        OptimizeError(
                            f"""Column '{col}' could not be resolved{f" in cte: '{cte}'" if cte else ' in main clause'}. Please qualify this column."""
                        )
                    ]
            for col in scope.unqualified_columns:
                cte = get_lowest_cte((col,))
                errors += [
                    OptimizeError(
                        f"""Ambiguous column '{col}' {f" in cte: '{cte}'" if cte else 'in main clause'}. Please qualify this column."""
                    )
                ]
    return errors


def qualify_sql_item(
    ast_: E, filtered_schema: dict[str, dict[str, str]], dialect: Dialect
) -> tuple[Expression, list[Exception]]:
    qualified = qualify(
        ast_,
        dialect=dialect,
        schema=filtered_schema,
        validate_qualify_columns=False,
        quote_identifiers=False,
        identify=False,
        infer_schema=True,
    )
    qualification_errors = validate_qualify_columns_errors(qualified)

    # try different qualification patterns if necessary
    if len(qualification_errors) > 0:
        qualified = qualify(
            qualified,
            dialect=dialect,
            validate_qualify_columns=False,
            quote_identifiers=False,
            identify=False,
            infer_schema=True,
        )
        qualification_errors = validate_qualify_columns_errors(qualified)
    return qualified, qualification_errors


def lineage_select(expression: E, sel: E) -> Expression:
    if isinstance(expression, exp.Select):
        select_ = t.cast(
            exp.Expression,
            expression.select(sel, append=False, copy=False),
        )
    else:
        select_ = expression.expression
    return select_


def add_sel_edge(
    g: DAG,
    tbl_name: str,
    sel: E,
    to_: str,
    ntype: list[str],
    datahub_nodes: bool = False,
):
    from_ = (str(tbl_name) + "." + sel.alias_or_name).replace('"', "")
    g.add_edge(from_, to_, {"ntype": set(ntype)})


def find_characters_between_equal_and_parenthesis(text):
    # Regex pattern to find characters (excluding spaces) between start or '=' and '('
    # It uses a character set [^\s]* that matches any characters except whitespace characters
    pattern = r"(?:^|(?<==))([^\s]*?)(?=\()"

    # Find all matches
    matches = re.findall(pattern, text)

    return matches


def union_helper(ast, name_override: str | None = None):
    name = name_override if name_override is not None else ast.alias
    union_search = list(ast.find_all(exp.Union))
    if len(union_search) > 0:
        unions = []
        for u in union_search:
            for attr in ["left", "right"]:
                new_ast = getattr(u, attr)
                new = [(name, new_ast)]
                if (
                    new not in unions
                    and new_ast is not None
                    and not isinstance(new_ast, exp.Union)
                ):
                    unions.extend(new)
        return unions
    else:
        new_ast = ast.this if isinstance(ast.this, exp.Select) else ast
        return [(name, new_ast)]


class SQLAstNode:
    append_key = "_" + _generate_random_ascii_string(10)
    join_str = "_____"

    def __init__(
        self,
        id: str = "",
        ast: Expression = Expression(),
        schema: dict[exp.Table, VinylSchema] = {},
        deps: list[str] = [],
        deps_schemas: dict[exp.Table, VinylSchema] = {},
        errors: list[VinylError] = [],
        dialect: Dialect = Dialect(),
        lineage: DAG | None = None,
        use_datahub_nodes: bool = False,
    ):
        self.id: str = id
        self.ast = ast
        self.original_ast = ast.copy()
        self.schema = schema
        self.deps = deps
        self.deps_schemas = deps_schemas
        self.dialect = dialect
        self.errors = errors
        self.lineage = lineage
        self.use_datahub_nodes = use_datahub_nodes

    def pre_qualify_transform(self, ast: Expression) -> Expression:
        if not isinstance(ast, exp.Table):
            return ast

        if not ast.catalog or not ast.db:
            return ast

        new_name = ""
        if ast.catalog is not None:
            new_name += ast.catalog + self.join_str
        if ast.db is not None:
            new_name += ast.db + self.join_str
        new_name += str(ast.this.this).replace(".", self.join_str) + self.append_key

        return exp.Table(
            catalog=None,
            name=None,
            this=exp.Identifier(this=new_name),
            alias=exp.TableAlias(this=ast.alias) if ast.alias else None,
        )

    def post_qualify_relabel(self, col_name: str) -> str:
        db_location, col_name = col_name.replace(self.append_key, "").rsplit(".", 1)
        db_location = ".".join(db_location.split(self.join_str))

        if not self.use_datahub_nodes:
            return db_location + "." + col_name

        dep_platforms = {}
        for id in [self.id, *self.deps]:
            name, platform = self.get_dataset_urn_info(id)
            dep_platforms[name] = platform

        platform = (
            dep_platforms.get(db_location) or self.get_dataset_urn_info(self.id)[-1]
        )
        dataset_urn = f"urn:li:dataset:({platform},{db_location},PROD)"
        schemafield_urn = f"urn:li:schemaField:({dataset_urn},{col_name})"
        return schemafield_urn

    @classmethod
    @lru_cache(maxsize=1000000)
    def get_dataset_urn_info(cls, id: str) -> tuple[str, str]:
        urn = DatasetUrn.from_string(id)
        return urn.name, urn.platform

    def qualify(self):
        self.ast = self.ast.transform(self.pre_qualify_transform)
        self.schema = get_sqlglot_schema(self.schema, self.pre_qualify_transform)
        self.deps_schemas = get_sqlglot_schema(
            self.deps_schemas, self.pre_qualify_transform
        )
        try:
            qualified = qualify(
                self.ast,
                dialect=self.dialect,
                schema=self.deps_schemas,
                validate_qualify_columns=False,
                quote_identifiers=False,
                identify=False,
                infer_schema=True,
            )
            qualification_errors = validate_qualify_columns_errors(qualified)

        except Exception as e:
            qualified = self.ast
            qualification_errors = [e]

        # try different qualification patterns if necessary
        if len(qualification_errors) > 0:
            try:
                qualified = qualify(
                    qualified,
                    dialect=self.dialect,
                    validate_qualify_columns=False,
                    quote_identifiers=False,
                    identify=False,
                    infer_schema=True,
                )
                qualification_errors = validate_qualify_columns_errors(qualified)
            except Exception as e:
                qualified = self.ast
                qualification_errors = [e]
        self.ast = qualified
        for e in qualification_errors:
            try:
                sql = self.original_ast.sql(pretty=True)
            except Exception:
                sql = "AST: " + self.original_ast.__repr__()

            self.errors += [
                VinylError(
                    node_id=self.id,
                    type=VinylErrorType.PARSE_ERROR,
                    msg=str(e),
                    dialect=self.dialect,
                    context=sql,
                )
            ]
        return self

    def optimize(self, rules: Sequence[Callable[..., Any]] = RULES):
        if self.errors != []:
            return self
        self = self.qualify()
        if self.errors != []:
            return self
        try:
            self.ast = optimize(
                self.ast,
                schema={k: v for k, v in self.deps_schemas.items() if v},
                dialect=self.dialect,
                rules=rules,
            )
        except Exception as e:
            self.errors.append(
                VinylError(
                    self.id,
                    (
                        VinylErrorType.OPTIMIZE_ERROR
                        if isinstance(e, OptimizeError)
                        else VinylErrorType.MISCELLANEOUS_ERROR
                    ),
                    str(e),
                    self.dialect,
                    self.original_ast.sql(pretty=True),
                )
            )

        return self

    def lineage_sources_helper(self):
        model_name = [k.this.this for k in self.schema][0]
        model_ast = self.ast.copy()
        sources = []
        for x in model_ast.find_all(exp.CTE):
            # split sources if there are unions
            sources += union_helper(x)
            x.pop()
        for x in model_ast.find_all(exp.With):
            x.pop()
        sources += union_helper(model_ast, model_name)
        # adjust table aliases and column qualifications to be trivial to make lineage parsing easier
        deps = [k.this.this for k in self.deps_schemas]
        for i, source in enumerate(sources):
            name, cte = source
            for tbl in cte.find_all(sge.Table):
                for col in cte.find_all(sge.Column):
                    previous_sources = [] if i == 0 else sources[: (i - 1)]
                    if (
                        col.table not in deps
                        and col.table
                        not in [j[0] for j in previous_sources if j[0] != name]
                        and col.table is not None
                        and col.table == tbl.alias
                    ):
                        col.set("table", tbl.name)
                if tbl.alias != "" and tbl.alias != tbl.name:
                    tbl.set("alias", tbl.name)
        return sources

    def get_lineage(self, lineage_filters: list[str] = [], overwrite: bool = False):
        if self.lineage is not None and not overwrite:
            return self.lineage

        self.lineage = DAG()

        sources = self.lineage_sources_helper()

        for k, cte in sources:
            scope = build_scope(cte)
            if not scope:
                continue
            # Get information for non-select columns
            wheres = []
            havings = []
            qualifies = []
            groupbys = []
            joins = []
            if not lineage_filters or "filter" in lineage_filters:
                for li in scope.find_all(exp.Where):
                    for lj in li.find_all(exp.Column):
                        wheres += [lj.sql(dialect=self.dialect, comments=False)]

                for li in scope.find_all(exp.Having):
                    for lj in li.find_all(exp.Column):
                        havings += [lj.sql(dialect=self.dialect, comments=False)]

                for li in scope.find_all(exp.Qualify):
                    for lj in li.find_all(exp.Column):
                        qualifies += [lj.sql(dialect=self.dialect, comments=False)]
            if not lineage_filters or "group_by" in lineage_filters:
                for li in scope.find_all(exp.Group):
                    for lj in li.find_all(exp.Column):
                        groupbys += [lj.sql(dialect=self.dialect, comments=False)]
            if not lineage_filters or "join_key" in lineage_filters:
                for li in scope.find_all(exp.Join):
                    if li.args.get("on") is not None:
                        for lj in li.args.get("on").find_all(exp.Column):
                            joins += [lj.sql(dialect=self.dialect, comments=False)]

            non_select = wheres + groupbys + havings + qualifies + joins
            non_select_type = (
                ["filter" for i in wheres]
                + ["group_by" for i in groupbys]
                + ["having" for i in havings]
                + ["qualify" for i in qualifies]
                + ["join_key" for i in joins]
            )

            # get named windows
            named_windows_cols = {}
            for w in scope.find_all(exp.Window):
                if w.name == "":
                    continue
                named_windows_cols[w.name] = [
                    c.sql(dialect=self.dialect, comments=False).replace('"', "")
                    for c in list(w.find_all(exp.Column))
                ]

            # build select graph
            expression = scope.expression
            if not hasattr(expression, "selects"):
                continue

            for sel in expression.selects:
                select_helper = lineage_select(expression, sel)
                if select_helper is None or not hasattr(select_helper, "selects"):
                    continue
                selects_ = select_helper.selects
                if len(selects_) == 0:
                    continue
                select_ = selects_[
                    0
                ]  # removes everything but the pure select clause (e.g. filters)

                # get select col type
                select_parse = find_characters_between_equal_and_parenthesis(
                    str(repr(select_))
                )
                select_parse_filter = [
                    i not in ["Select", "Alias", "Column", "Identifier", "DataType"]
                    for i in select_parse
                ]
                if any(select_parse_filter):
                    select_type = "transform"
                else:
                    select_type = "as_is"

                # build select graph
                if not lineage_filters or select_type in lineage_filters:
                    for c in select_.find_all(exp.Column):
                        add_sel_edge(
                            self.lineage,
                            k,
                            sel,
                            c.sql(dialect=self.dialect, comments=False)
                            .replace('"', "")
                            .replace("`", ""),
                            [select_type],
                        )

                # handle aliased windows
                if not lineage_filters or "transform" in lineage_filters:
                    for w in select_.find_all(exp.Window):
                        if w.alias != "" and w.alias in named_windows_cols:
                            for col_name in named_windows_cols[w.alias]:
                                add_sel_edge(
                                    self.lineage,
                                    k,
                                    sel,
                                    col_name,
                                    ["transform"],
                                )

                # build non-select graph
                for i, c2 in enumerate(non_select):
                    add_sel_edge(
                        self.lineage,
                        k,
                        sel,
                        c2.replace('"', "").replace("`", ""),
                        [non_select_type[i]],
                    )

        # remove trivial nodes
        ids = [ix.this.this for ix in {**self.deps_schemas, **self.schema}]
        id_replace_dict = {
            x.lower() if str(self.dialect) != "snowflake" else x.upper(): x for x in ids
        }
        # remove all nodes that are not from dependent tables, have blank column names, are wildcards, or are malformed tables. In this case, malformed means they contain periods but are also direct database references. Vinyl tables can contain periods but won't be from the db.
        nodes_to_remove = [
            x
            for x in self.lineage.node_dict
            if (x.rsplit(".", 1)[0] not in id_replace_dict and self.append_key not in x)
            or "." not in x
            or x.rsplit(".", 1)[1].startswith("*")
            or ("." in x.rsplit(".", 1)[0] and self.append_key in x)
        ]
        try:
            self.lineage.remove_nodes_and_reconnect(nodes_to_remove)
        except Exception as e:
            self.errors.append(
                VinylError(
                    self.id,
                    VinylErrorType.CYCLE_ERROR,
                    str(e),
                    self.dialect,
                    self.original_ast.sql(pretty=True),
                )
            )
            self.lineage = DAG()
            return self

        # get correct case again
        self.lineage = self.lineage.relabel(lambda x: self.post_qualify_relabel(x))

        # add nodes for all columns in table_graph, even if they have no connections or have errors:
        all_schemas = {**self.deps_schemas, **self.schema}
        for node, schema in all_schemas.items():
            # convert all schemas to regular dicts, if they haven't already been
            if isinstance(schema, VinylSchema):
                schema = dict(schema.items())
            for colname in schema:
                if colname is None or colname == "" or "." in colname:
                    continue
                graph_name = f"{node.this.this}.{colname}"
                if self.use_datahub_nodes:
                    graph_name = self.post_qualify_relabel(graph_name)
                if (
                    graph_name not in self.lineage.node_dict
                ):  # remove subcolumns for now
                    self.lineage.add_node(graph_name)

        return self.lineage.reverse()


class SQLProject:
    def __init__(self, nodes: list[SQLAstNode], db_graph: DAG):
        self.nodes = nodes
        self.db_graph = db_graph

    def optimize(self):
        for node in self.nodes:
            node.optimize()

        return self

    def get_lineage(self, lineage_filters: list[str] = []):
        for node in self.nodes:
            node.get_lineage(lineage_filters)

        return self

    def stitch_lineage(
        self,
        ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
    ) -> dict[str, Any]:
        col_lineages = []
        errors = []
        selected = self._select_nodes(ids, predecessor_depth, successor_depth)
        parents = self.db_graph.get_parents(selected)
        table_lineage = self.db_graph.subgraph(
            list(set(selected + parents))
        ).to_networkx()
        for id in selected:
            for node in self.nodes:
                if node.id == id:
                    lineage = node.get_lineage()

                    # add schema to table lineage nodes
                    table_lineage.nodes[id]["schema"] = {
                        name: type(coltype).__name__
                        for name, coltype in node.schema.items()
                    }
                    for tablename, schema in node.deps_schemas.items():
                        table_lineage.nodes[tablename.this.this]["schema"] = {
                            name: type(coltype).__name__
                            for name, coltype in schema.items()
                        }
                    errors.extend(node.errors)
                    if lineage is not None:
                        col_lineages.append(lineage.to_networkx())

        return {
            "errors": errors,
            "table_lineage": nx.node_link_data(table_lineage),
            "column_lineage": nx.node_link_data(nx.compose_all(col_lineages)),
        }

    def stitch_lineage_postgres(
        self,
        ids: list[str] | None = None,
        predecessor_depth: int | None = None,
        successor_depth: int | None = None,
    ):
        selected = self._select_nodes(ids, predecessor_depth, successor_depth)
        columns = []
        column_links = []
        for id in selected:
            for node in self.nodes:
                if node.id == id:
                    for name, coltype in node.schema.items():
                        col = {
                            "table_unique_name": node.id,
                            "name": name,
                            "type": str(coltype),
                        }
                        if col not in columns:
                            columns.append(col)
                    for tablename, schema in node.deps_schemas.items():
                        # if ".sources." in tablename:
                        for name, coltype in schema.items():
                            col = {
                                "table_unique_name": tablename,
                                "name": name,
                                "type": str(coltype),
                            }
                            if col not in columns:
                                columns.append(col)

                    full_lineage = node.get_lineage()
                    if not full_lineage:
                        continue

                    for source_index, target_index in full_lineage.g.edge_list():
                        source = full_lineage.node_dict.inv[source_index]
                        target = full_lineage.node_dict.inv[target_index]
                        column_links.append(
                            {
                                "source_name": source,
                                "target_name": target,
                                "lineage_type": "all",
                                "connection_types": list(
                                    full_lineage.g.get_edge_data(
                                        source_index, target_index
                                    )["ntype"]
                                ),
                            }
                        )
                    direct_lineage = node.get_lineage(
                        lineage_filters=["as-is", "transform"]
                    )
                    if not direct_lineage:
                        continue
                    for source_index, target_index in direct_lineage.g.edge_list():
                        source = direct_lineage.node_dict.inv[source_index]
                        target = direct_lineage.node_dict.inv[target_index]
                        column_links.append(
                            {
                                "source_name": source,
                                "target_name": target,
                                "lineage_type": "direct_only",
                                "connection_types": list(
                                    full_lineage.g.get_edge_data(
                                        source_index, target_index
                                    )["ntype"]
                                ),
                            }
                        )
        return columns, column_links

    def _select_nodes(self, ids, predecessor_depth, successor_depth):
        if ids is None:
            nodes = self.db_graph.topological_sort()
        else:
            nodes_to_consider = self.db_graph.get_ancestors_and_descendants(
                ids, predecessor_depth, successor_depth
            )
            nodes = self.db_graph.subgraph(list(nodes_to_consider)).topological_sort()
        nodes = [n for n in nodes if not isinstance(n, VinylTable)]
        return nodes

    def get_errors(self) -> list[VinylError]:
        errors = []
        for node in self.nodes:
            for error in node.errors:
                if error not in errors:
                    errors.append(error)
        return errors
