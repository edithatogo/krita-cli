"""Rollback CLI command."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command()
def rollback(
    ctx: Context,
    batch_id: Annotated[str, typer.Argument(help="ID of the batch to roll back")],
) -> None:
    """Roll back a previously executed batch.

    This restores the canvas to its state before the specified batch was executed.
    Note that snapshots are kept in memory and are lost if the Krita plugin is restarted.
    """
    try:
        client = _shared._get_client(ctx)
        result = client.rollback(batch_id=batch_id)
        console.print(json.dumps(result, indent=2, default=str))
    except KritaError as exc:
        _shared._handle_error(exc)
