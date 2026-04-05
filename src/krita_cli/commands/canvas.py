"""Canvas-related CLI commands: new-canvas, get-canvas, save, clear."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command("new-canvas")
def new_canvas(
    ctx: Context,
    width: Annotated[int, typer.Option("--width", "-W", help="Canvas width in pixels")] = 800,
    height: Annotated[int, typer.Option("--height", "-H", help="Canvas height in pixels")] = 600,
    name: Annotated[str, typer.Option("--name", "-n", help="Document name")] = "New Canvas",
    background: Annotated[str, typer.Option("--background", "-b", help="Background color (hex)")] = "#1a1a2e",
) -> None:
    """Create a new canvas in Krita."""
    try:
        client = _shared._get_client(ctx)
        result = client.new_canvas(width=width, height=height, name=name, background=background)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("get-canvas")
def get_canvas(
    ctx: Context,
    filename: Annotated[str, typer.Option("--filename", "-f", help="Output filename")] = "canvas.png",
) -> None:
    """Export the current canvas to a PNG file."""
    console.print("[dim]Exporting canvas (this may take a while for large canvases)...[/dim]")
    try:
        client = _shared._get_client(ctx)
        result = client.get_canvas(filename=filename)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command()
def save(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Full file path to save to")],
) -> None:
    """Save the current canvas to a specific file path."""
    console.print("[dim]Saving canvas (this may take a while for large canvases)...[/dim]")
    try:
        client = _shared._get_client(ctx)
        result = client.save(path=path)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command()
def clear(
    ctx: Context,
    color: Annotated[str, typer.Option("--color", "-c", help="Color to fill with")] = "#1a1a2e",
) -> None:
    """Clear the canvas to a solid color."""
    try:
        client = _shared._get_client(ctx)
        result = client.clear(color=color)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
