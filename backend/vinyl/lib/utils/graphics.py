import builtins
import os

import ibis.expr.datatypes as dt
import rich
from ibis import Schema
from rich.console import Console
from rich.table import Table
from rich.text import Text
from textual.app import App
from textual.binding import Binding

from vinyl.lib.utils.context import _is_notebook

original_print = builtins.print


def _adjust_type(type: dt.DataType) -> Text:
    if type.is_numeric():
        return Text(str(type), style="yellow")
    elif type.is_string():
        return Text(str(type), style="orange1")
    elif type.is_temporal():
        return Text(str(type), style="cyan")
    elif type.is_boolean():
        return Text(str(type), style="purple")
    elif type.is_json() or type.is_struct() or type.is_array():
        return Text(str(type), style="bright_magenta")
    elif type.is_uuid():
        return Text(str(type), style="medium_purple1")
    elif type.is_geospatial():
        return Text(str(type), style="dark_goldenrod")
    else:
        return Text(str(type))


def _print_schema(schema: Schema) -> Table:
    out = Table()
    out.add_column("#")
    out.add_column("column")
    out.add_column("type")
    for i, (name, type_) in enumerate(schema.items()):
        out.add_row(str(i), str(name), _adjust_type(type_))

    return out


def rich_print(*args, **kwargs):
    if os.getenv("PLAIN_PRINT", "false") == "true":
        original_print(*args, **kwargs)
    elif _is_notebook():
        try:
            console = Console(width=10000)
            console.print(*args, **kwargs)
        except Exception:
            original_print(*args, **kwargs)
    else:
        try:
            rich.print(*args, **kwargs)
        except Exception:
            original_print(*args, **kwargs)


class TurntableTextualApp(App):
    _BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="r", action="reload", description="Reload"),
        Binding(key="d", action="toggle_dark", description="Toggle Dark Mode"),
    ]

    def action_reload(self) -> None:
        self.mount()
