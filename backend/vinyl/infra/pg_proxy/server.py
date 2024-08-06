import os
import sys
from typing import Tuple
import sqlglot

import duckdb

from vinyl.infra.pg_proxy.backends.duckdb import DuckDBConnection
from vinyl.infra.pg_proxy.bv_dialects import BVPostgres, BVDuckDB
from vinyl.infra.pg_proxy.postgres import ProxyServer
from vinyl.infra.pg_proxy.rewrite import Rewriter


class TurntableMetricsRewriter(Rewriter):
    def rewrite(self, sql: str) -> str:
        if sql.lower() == "select pg_catalog.version()":
            return "SELECT 'PostgreSQL 9.3' as version"

        ast = sqlglot.parse_one(sql)
        tables = [t for t in ast.find_all(sqlglot.expressions.Table)]

        metric_ctes = []
        for table in tables:
            if table.db == "metrics":
                # todo: get the real metrics code from ibis here
                cte_sql = "SELECT * FROM source"
                cte_name = f"metrics_{table.name}"
                # cte = sqlglot.parse_one(
                #     f"WITH {cte_name} AS ({cte_sql}) SELECT 1"
                # ).find(sqlglot.expressions.CTE)
                metric_ctes.append((cte_name, cte_sql))

        if len(metric_ctes) > 0:
            for alias, sql in metric_ctes:
                ## todo: clean this up with sqlglot functions to handle prepend
                metrics_sql = f"WITH {alias} AS ( {sql} ) {ast.sql()};"
            return super().rewrite(metrics_sql)

        return super().rewrite(sql)


rewriter = TurntableMetricsRewriter(BVPostgres(), BVDuckDB())


def create(
    db: duckdb.DuckDBPyConnection, host_addr: Tuple[str, int], auth: dict = None
) -> ProxyServer:
    server = ProxyServer(host_addr, DuckDBConnection(db), rewriter=rewriter, auth=auth)
    return server


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("(Turntable) Using in-memory DuckDB")
        db = duckdb.connect()
    else:
        print("(Turntable) Using DuckDB database at %s" % sys.argv[1])
        db = duckdb.connect(sys.argv[1])

    bv_host = "0.0.0.0"
    bv_port = 5433

    if "HOST" in os.environ:
        bv_host = os.environ["HOST"]

    if "PORT" in os.environ:
        bv_port = int(os.environ["PORT"])

    address = (bv_host, bv_port)
    server = create(db, address)
    ip, port = server.server_address
    print(f"Listening on {ip}:{port}")

    try:
        server.serve_forever()
    finally:
        server.shutdown()
        db.close()
