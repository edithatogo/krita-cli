import typer
from rich.console import Console
from typing import Annotated
from typer import Context

from krita_cli import _shared

app = typer.Typer()
console = Console()


@app.command("select-rect")
def select_rect(
    ctx: Context,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    """Select a rectangular area."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_rect(x=x, y=y, width=width, height=height)
        _shared._print_result(result, f"Selected rectangle {width}x{height} at ({x}, {y})")


@app.command("select-ellipse")
def select_ellipse(
    ctx: Context,
    cx: int,
    cy: int,
    rx: int,
    ry: int,
) -> None:
    """Select an elliptical area."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_ellipse(cx=cx, cy=cy, rx=rx, ry=ry)
        _shared._print_result(result, f"Selected ellipse at ({cx}, {cy}) with radii {rx}x{ry}")


@app.command("select-polygon")
def select_polygon(
    ctx: Context,
    points: list[str],
) -> None:
    """Select a polygonal area. Points as 'x,y' pairs (min 3)."""
    parsed: list[list[int]] = []
    for pt in points:
        parts = pt.split(",")
        if len(parts) != 2:
            console.print(f"[red]Error:[/red] Invalid point format: {pt!r}. Use 'x,y'.")
            raise typer.Exit(code=1)
        try:
            parsed.append([int(parts[0]), int(parts[1])])
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid point coordinates: {pt!r}. Values must be integers.")
            raise typer.Exit(code=1) from None

    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_polygon(points=parsed)
        _shared._print_result(result, f"Selected polygon with {len(parsed)} points")


@app.command("select-area")
def select_area_compat(
    ctx: Context,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    """Select a rectangular area.

    Deprecated: prefer `krita select-rect` instead. This alias will be
    removed in a future release.
    """
    select_rect(ctx, x, y, width, height)


@app.command("select-clear")
def clear_selection(ctx: Context) -> None:
    """Clear the content of the current selection."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.clear_selection()
        _shared._print_result(result, "Cleared selection")


@app.command("select-invert")
def invert_selection(ctx: Context) -> None:
    """Invert the current selection."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.invert_selection()
        _shared._print_result(result, "Inverted selection")


@app.command("select-fill")
def fill_selection(ctx: Context) -> None:
    """Fill the current selection with foreground color."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.fill_selection()
        _shared._print_result(result, "Filled selection")


@app.command("select-info")
def selection_info(ctx: Context) -> None:
    """Get information about the current selection."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.selection_info()
        if result.get("has_selection"):
            bounds = result.get("bounds", {})
            console.print(f"[green]Active selection:[/green] x={bounds.get('x')}, y={bounds.get('y')}, "
                          f"w={bounds.get('width')}, h={bounds.get('height')}")
        else:
            console.print("[dim]No active selection[/dim]")


@app.command("deselect")
def deselect(ctx: Context) -> None:
    """Remove the current selection."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.deselect()
        _shared._print_result(result, "Deselected")


@app.command("transform-selection")
def transform_selection(
    ctx: Context,
    dx: Annotated[int, typer.Option("--dx", help="Horizontal offset")] = 0,
    dy: Annotated[int, typer.Option("--dy", help="Vertical offset")] = 0,
    angle: Annotated[float, typer.Option("--angle", "-a", help="Rotation angle in degrees")] = 0.0,
    scale_x: Annotated[float, typer.Option("--scale-x", help="Horizontal scale factor")] = 1.0,
    scale_y: Annotated[float, typer.Option("--scale-y", help="Vertical scale factor")] = 1.0,
) -> None:
    """Transform the current selection (move, rotate, scale)."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.transform_selection(dx=dx, dy=dy, angle=angle, scale_x=scale_x, scale_y=scale_y)
        _shared._print_result(result, f"Transformed selection (dx={dx}, dy={dy}, angle={angle}°)")


@app.command("grow-selection")
def grow_selection(
    ctx: Context,
    pixels: Annotated[int, typer.Argument(help="Pixels to grow")],
) -> None:
    """Grow the current selection outward."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.grow_selection(pixels)
        _shared._print_result(result, f"Grew selection by {pixels}px")


@app.command("shrink-selection")
def shrink_selection(
    ctx: Context,
    pixels: Annotated[int, typer.Argument(help="Pixels to shrink")],
) -> None:
    """Shrink the current selection inward."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.shrink_selection(pixels)
        _shared._print_result(result, f"Shrunk selection by {pixels}px")


@app.command("border-selection")
def border_selection(
    ctx: Context,
    pixels: Annotated[int, typer.Argument(help="Border width in pixels")],
) -> None:
    """Create a border selection around the current selection."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.border_selection(pixels)
        _shared._print_result(result, f"Created {pixels}px border around selection")
