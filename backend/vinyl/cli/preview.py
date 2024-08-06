import threading
from typing import Optional

import typer
from textual.app import ComposeResult
from textual.widgets import DataTable, Footer
from vinyl import Field
from vinyl.lib.constants import PreviewHelper
from vinyl.lib.definitions import _load_project_defs
from vinyl.lib.erd import create_erd_app
from vinyl.lib.project import Project
from vinyl.lib.query_engine import QueryEngine
from vinyl.lib.utils.graphics import TurntableTextualApp

preview_cli: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)


class PreviewTable(TurntableTextualApp):
    def __init__(self, rows, columns, shutdown_seconds: Optional[int] = None):
        self._rows = rows
        self._columns = columns
        self._shutdown_seconds = shutdown_seconds
        super().__init__()

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self._columns)
        table.add_rows(self._rows)
        if self._shutdown_seconds:
            threading.Timer(self._shutdown_seconds, self.quit).start()

    def quit(self):
        self.exit()


@preview_cli.command("model")
def preview_model(
    name: str = typer.Option(
        False, "--name", "-m", help="exported name of the model or source"
    ),
    twin: bool = typer.Option(False, "--twin", "-t", help="use twin data"),
    limit: int = typer.Option(1000, "--limit", "-l", help="limit the number of rows"),
    shutdown_seconds: Optional[int] = typer.Option(
        None, "--shutdown", "-s", help="shutdown after n seconds. Default is None."
    ),
):
    """Preview a model"""
    # track = EventLogger()
    # track.log_event(Event.PREVIEW_MODEL)
    if twin:
        PreviewHelper._preview = "twin"

    project = Project.bootstrap()
    query_engine = QueryEngine(project)
    if isinstance(limit, typer.models.OptionInfo):
        # handle typing of default value for limit
        if limit.default is None:
            raise ValueError("limit must have a default that is an integer")
        limit = limit.default
    result = query_engine._model(name, limit=limit)
    app = PreviewTable(
        columns=tuple(result.columns()),
        rows=result.numpy_rows(),
        shutdown_seconds=shutdown_seconds,
    )
    app.run()


@preview_cli.command("metric")
def preview_metric(
    name: str = typer.Option(..., help="exported name of the metric column"),
    grain: str = typer.Option(
        ..., help="grain to bucket the metric by (ex: months=3, year=1)"
    ),
    dims: list[str] = typer.Option(
        None, "--dims", help="comma separated list of dimensions to include"
    ),
    cols: list[str] = typer.Option(
        None, "--cols", help="comma separated list of columns to include"
    ),
    shutdown_seconds: Optional[int] = typer.Option(
        None, "--shutdown", "-s", help="shutdown after n seconds. Default is None."
    ),
):
    """Preview a model"""
    # track = EventLogger()
    # track.log_event(Event.PREVIEW_METRIC)
    project = Project.bootstrap()
    query_engine = QueryEngine(project)
    result = query_engine._metric(store=name, grain=grain, limit=1000)

    app = PreviewTable(
        columns=result.columns(),
        rows=result.numpy_rows(),
        shutdown_seconds=shutdown_seconds,
    )
    app.run()


@preview_cli.command("erd")
def erd(
    names: list[str] = typer.Option(
        [], "--name", "-m", help="exported name(s) of the model or source"
    ),
):
    """Generate an ERD"""
    _load_project_defs()
    G = Field._export_relations_to_networkx(
        shorten_name=True, filter=None if len(names) == 0 else names
    )
    create_erd_app(G).run()
