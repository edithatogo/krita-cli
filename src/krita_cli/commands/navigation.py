"""Navigation-related CLI commands: undo, redo."""

from __future__ import annotations

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

app = typer.Typer()


@app.command()
def undo(ctx: Context) -> None:
    """Undo the last action."""
    try:
        client = _shared._get_client(ctx)
        result = client.undo()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command()
def redo(ctx: Context) -> None:
    """Redo the last undone action."""
    try:
        client = _shared._get_client(ctx)
        result = client.redo()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
