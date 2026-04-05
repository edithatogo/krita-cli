"""Krita CLI — Main application composition."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from typer import Context

from krita_cli import _shared
from krita_cli.commands import config as _config
from krita_client import (
    KritaCommandError,
    KritaConnectionError,
    KritaValidationError,
)

app = typer.Typer(
    name="krita",
    help="CLI for programmatic painting in Krita via the MCP plugin.",
    no_args_is_help=True,
    add_completion=False,
)
app.add_typer(_config.app, name="config")
console = _shared.console

# Re-export shared utilities for backward compatibility
CLIState = _shared.CLIState
_handle_error = _shared._handle_error
_get_client = _shared._get_client
_format_result = _shared._format_result


# -- Global options -----------------------------------------------------------


@app.callback()
def callback(
    ctx: Context,
    url: Annotated[
        str | None,
        typer.Option("--url", "-u", help="Krita plugin URL (overrides KRITA_URL env var)"),
    ] = None,
    record: Annotated[
        str | None,
        typer.Option("--record", "-r", help="Record commands to a JSON file"),
    ] = None,
) -> None:
    """Krita CLI — programmatic painting in Krita."""
    ctx.obj = CLIState()
    ctx.obj.url = url
    ctx.obj.record = record


# -- Register sub-apps --------------------------------------------------------
# Lazy imports to avoid circular dependency between app.py and command modules.
from krita_cli.commands import (
    batch as _batch,
)
from krita_cli.commands import (
    brush as _brush,
)
from krita_cli.commands import (
    call as _call,
)
from krita_cli.commands import (
    canvas as _canvas,
)
from krita_cli.commands import (
    color as _color,
)
from krita_cli.commands import (
    file_ops as _file_ops,
)
from krita_cli.commands import (
    health as _health,
)
from krita_cli.commands import (
    history as _history,
)
from krita_cli.commands import (
    history_cmd as _history_cmd,
)
from krita_cli.commands import (
    introspect as _introspect,
)
from krita_cli.commands import (
    navigation as _navigation,
)
from krita_cli.commands import (
    replay as _replay,
)
from krita_cli.commands import (
    rollback as _rollback,
)
from krita_cli.commands import (
    selection as _selection,
)
from krita_cli.commands import (
    stroke as _stroke,
)

app.add_typer(_canvas.app)
app.add_typer(_color.app)
app.add_typer(_brush.app)
app.add_typer(_stroke.app)
app.add_typer(_navigation.app)
app.add_typer(_file_ops.app)
app.add_typer(_health.app)
app.add_typer(_call.app)
app.add_typer(_history.app)
app.add_typer(_history_cmd.app)
app.add_typer(_batch.app)
app.add_typer(_rollback.app)
app.add_typer(_introspect.app)
app.add_typer(_replay.app)
app.add_typer(_selection.app)

# Re-export command functions for backward compatibility (cli.py shim)
new_canvas = _canvas.new_canvas
get_canvas = _canvas.get_canvas
save = _canvas.save
clear = _canvas.clear
set_color = _color.set_color
get_color_at = _color.get_color_at
set_brush = _brush.set_brush
list_brushes = _brush.list_brushes
stroke = _stroke.stroke
fill = _stroke.fill
draw_shape = _stroke.draw_shape
undo = _navigation.undo
redo = _navigation.redo
open_file = _file_ops.open_file
health = _health.health
call = _call.call


# -- Entry point --------------------------------------------------------------


def main() -> None:  # pragma: no cover
    """Main entry point for the CLI."""
    try:
        app()
    except (KritaConnectionError, KritaCommandError, KritaValidationError) as exc:
        _handle_error(exc)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/dim]")
        sys.exit(130)


if __name__ == "__main__":  # pragma: no cover
    main()
