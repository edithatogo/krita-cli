"""Brush-related CLI commands: set-brush, list-brushes."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command("set-brush")
def set_brush(
    ctx: Context,
    preset: Annotated[str | None, typer.Option("--preset", "-p", help="Brush preset name")] = None,
    size: Annotated[int | None, typer.Option("--size", "-s", help="Brush size in pixels")] = None,
    opacity: Annotated[float | None, typer.Option("--opacity", "-o", help="Brush opacity (0.0-1.0)")] = None,
) -> None:
    """Set brush preset and properties."""
    try:
        client = _shared._get_client(ctx)
        result = client.set_brush(preset=preset, size=size, opacity=opacity)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("list-brushes")
def list_brushes(
    ctx: Context,
    filter: Annotated[str, typer.Option("--filter", "-f", help="Filter by name")] = "",  # noqa: A002
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum number to return")] = 20,
) -> None:
    """List available brush presets."""
    try:
        client = _shared._get_client(ctx)
        result = client.list_brushes(filter=filter, limit=limit)
        brushes_raw = result.get("brushes", [])
        brushes = list(brushes_raw) if isinstance(brushes_raw, list) else []
        if not brushes:
            console.print("No brushes found matching filter.")
            return
        table = Table(title=f"Available Brushes ({len(brushes)})")
        table.add_column("#", style="dim")
        table.add_column("Name")
        for i, name in enumerate(brushes, 1):
            table.add_row(str(i), name)
        console.print(table)
    except KritaError as exc:
        _shared._handle_error(exc)
