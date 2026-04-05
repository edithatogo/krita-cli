"""Selection-related CLI commands: select-area, clear-selection, fill-selection, deselect."""

from __future__ import annotations

from typing import Annotated

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

app = typer.Typer()


@app.command("area")
def select_area(
    ctx: Context,
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
    width: Annotated[int, typer.Option("--width", "-W", help="Selection width")],
    height: Annotated[int, typer.Option("--height", "-H", help="Selection height")],
) -> None:
    """Select a rectangular area on the canvas."""
    try:
        client = _shared._get_client(ctx)
        result = client.select_area(x=x, y=y, width=width, height=height)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("clear")
def clear_selection(ctx: Context) -> None:
    """Clear the contents of the current selection."""
    try:
        client = _shared._get_client(ctx)
        result = client.clear_selection()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("fill")
def fill_selection(ctx: Context) -> None:
    """Fill the current selection with the foreground color."""
    try:
        client = _shared._get_client(ctx)
        result = client.fill_selection()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command()
def deselect(ctx: Context) -> None:
    """Remove the current selection."""
    try:
        client = _shared._get_client(ctx)
        result = client.deselect()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
