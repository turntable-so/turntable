import math
import os
from multiprocessing import Process

import duckdb
import ibis
import typer
from rich import print

from vinyl.cli.events import Event, EventLogger
from vinyl.infra.pg_proxy.server import create as create_pg_proxy
from vinyl.lib.definitions import _load_project_defs
from vinyl.lib.metric import MetricStore
from vinyl.lib.project import Project

project_cli: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)


def _format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_names = (
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
        "PB",
    )
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


@project_cli.command("deploy")
def deploy():
    """Deploy a Vinyl project"""
    track = EventLogger()
    track.log_event(Event.DEPLOY)
    defs = _load_project_defs()
    if not os.path.exists(".vinyl"):
        os.makedirs(".vinyl")
    if os.path.exists(".vinyl/vinyl.duckdb"):
        os.remove(".vinyl/vinyl.duckdb")

    conn = ibis.duckdb.connect(".vinyl/vinyl.duckdb")
    project = Project(resources=defs.resources, models=defs.models)

    deployed_models = []
    for model in project.models:
        table = model()
        if isinstance(table, MetricStore):
            # we dont support this yet
            continue

        conn.create_table(model.__name__, table.execute("pyarrow"))
        deployed_models.append(model.__name__)
    print(f"Deployed models ({len(deployed_models)}):")
    for model in deployed_models:
        print(f"- {model}")

    print("\n")
    datasize = os.path.getsize("./.vinyl/vinyl.duckdb")
    print(f"total data size: {_format_size(datasize)}")


def proxy_server(db_path, bv_host, bv_port):
    import duckdb

    conn = duckdb.connect(db_path)
    server = create_pg_proxy(conn, (bv_host, bv_port))
    ip, port = server.server_address
    print(f"[green bold]ready[/green bold] Postgres proxy listening on {ip}:{port}")
    server.serve_forever()


def run_pg_proxy(db_path, bv_host, bv_port):
    p = Process(target=proxy_server, args=(db_path, bv_host, bv_port))
    p.start()
    return p


def http_server():
    import uvicorn

    from vinyl.infra.http_server.server import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_fast_api_process():
    p = Process(
        target=http_server,
    )
    p.start()
    return p


@project_cli.command("serve")
def serve():
    """Serve a Vinyl project"""
    bv_host = "0.0.0.0"
    bv_port = 5433
    db_path = ".vinyl/vinyl.duckdb"
    track = EventLogger()
    track.log_event(Event.SERVE)
    if not os.path.exists(db_path):
        raise RuntimeError(f"No database found in {db_path}")

    print(f"Using DuckDB database at {db_path}\n")
    print("Tables:")
    conn = duckdb.connect(db_path)
    tables = conn.execute("show tables;").fetchall()
    for table in tables:
        print(f"- {table[0]}")
    print()
    conn.close()

    try:
        pg_proxy_process = run_pg_proxy(db_path, bv_host, bv_port)
        fast_api_process = run_fast_api_process()
        fast_api_process.join()
        pg_proxy_process.join()

    finally:
        pg_proxy_process.terminate()
