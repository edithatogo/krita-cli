"""Canvas introspection CLI commands: canvas-info, current-color, current-brush."""

from __future__ import annotations

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = _shared.console

app = typer.Typer()


@app.command("canvas-info")
def canvas_info(ctx: Context) -> None:
    """Get information about the current canvas."""
    try:
        client = _shared._get_client(ctx)
        result = client.get_canvas_info()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("current-color")
def current_color(ctx: Context) -> None:
    """Get the current foreground and background colors."""
    try:
        client = _shared._get_client(ctx)
        result = client.get_current_color()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("current-brush")
def current_brush(ctx: Context) -> None:
    """Get the current brush preset and properties."""
    try:
        client = _shared._get_client(ctx)
        result = client.get_current_brush()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
