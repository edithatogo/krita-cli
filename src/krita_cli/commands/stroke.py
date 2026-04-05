"""Stroke-related CLI commands: stroke, fill, draw-shape."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command()
def stroke(
    ctx: Context,
    points: Annotated[list[str], typer.Argument(help="Points as 'x,y' pairs (need at least 2)")],
    pressure: Annotated[float, typer.Option("--pressure", help="Brush pressure (0.0-1.0)")] = 1.0,
    size: Annotated[int | None, typer.Option("--size", "-s", help="Brush size in pixels")] = None,
    hardness: Annotated[float, typer.Option("--hardness", help="Stroke hardness (0.0-1.0)")] = 0.5,
    opacity: Annotated[float, typer.Option("--opacity", "-o", help="Stroke opacity (0.0-1.0)")] = 1.0,
) -> None:
    """Paint a stroke through a series of points."""
    parsed_points: list[list[int]] = []
    for pt in points:
        parts = pt.split(",")
        if len(parts) != 2:
            console.print(f"[red]Error:[/red] Invalid point format: {pt!r}. Use 'x,y'.")
            raise typer.Exit(code=1)
        parsed_points.append([int(parts[0]), int(parts[1])])

    try:
        client = _shared._get_client(ctx)
        result = client.stroke(
            points=parsed_points,
            pressure=pressure,
            size=size,
            hardness=hardness,
            opacity=opacity,
        )
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command()
def fill(
    ctx: Context,
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
    radius: Annotated[int, typer.Option("--radius", "-r", help="Fill radius in pixels")] = 50,
) -> None:
    """Fill a circular area with the current color."""
    try:
        client = _shared._get_client(ctx)
        result = client.fill(x=x, y=y, radius=radius)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("draw-shape")
def draw_shape(
    ctx: Context,
    shape: Annotated[str, typer.Argument(help="Shape type: rectangle, ellipse, or line")],
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
    width: Annotated[int, typer.Option("--width", "-W", help="Width")] = 100,
    height: Annotated[int, typer.Option("--height", "-H", help="Height")] = 100,
    *,
    fill: Annotated[bool, typer.Option("--fill/--no-fill", help="Fill the shape")] = True,
    stroke: Annotated[bool, typer.Option("--stroke/--no-stroke", help="Draw outline")] = False,
    x2: Annotated[int | None, typer.Option("--x2", help="End X for lines")] = None,
    y2: Annotated[int | None, typer.Option("--y2", help="End Y for lines")] = None,
) -> None:
    """Draw a shape on the canvas."""
    try:
        client = _shared._get_client(ctx)
        result = client.draw_shape(
            shape=shape,
            x=x,
            y=y,
            width=width,
            height=height,
            fill=fill,
            stroke=stroke,
            x2=x2,
            y2=y2,
        )
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
