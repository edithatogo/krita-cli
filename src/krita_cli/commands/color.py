"""Color-related CLI commands: set-color, get-color-at."""

from __future__ import annotations

from typing import Annotated

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

app = typer.Typer()


@app.command("set-color")
def set_color(
    ctx: Context,
    color: Annotated[str, typer.Argument(help="Hex color code (e.g., #ff6b6b)")],
) -> None:
    """Set the foreground paint color."""
    try:
        client = _shared._get_client(ctx)
        result = client.set_color(color=color)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("get-color-at")
def get_color_at(
    ctx: Context,
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
) -> None:
    """Sample the color at a specific pixel (eyedropper)."""
    try:
        client = _shared._get_client(ctx)
        result = client.get_color_at(x=x, y=y)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
