"""File operation CLI commands: open-file."""

from __future__ import annotations

from typing import Annotated

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

app = typer.Typer()


@app.command("open-file")
def open_file(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Full file path to open")],
) -> None:
    """Open an existing file in Krita (.kra, .png, .jpg, etc)."""
    try:
        client = _shared._get_client(ctx)
        result = client.open_file(path=path)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
