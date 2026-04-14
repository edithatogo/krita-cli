from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
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


@app.command("select-by-color")
def select_by_color(
    ctx: Context,
    x: Annotated[int | None, typer.Option("--x", "-x", help="X coordinate for magic wand (omit for global)")] = None,
    y: Annotated[int | None, typer.Option("--y", "-y", help="Y coordinate for magic wand (omit for global)")] = None,
    tolerance: Annotated[float, typer.Option("--tolerance", "-t", help="Color tolerance (0.0-1.0)", min=0.0, max=1.0)] = 0.1,
    contiguous: Annotated[bool, typer.Option("--contiguous/--global", "-c/-g", help="Contiguous (magic wand) or global selection")] = True,
) -> None:
    """Select pixels by color similarity (magic wand or global)."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_by_color(x=x, y=y, tolerance=tolerance, contiguous=contiguous)
        method = "Magic wand" if contiguous else "Global"
        count = result.get("selected_count", 0)
        _shared._print_result(result, f"{method} color selection: {count} pixels (tolerance={tolerance})")


@app.command("select-by-alpha")
def select_by_alpha(
    ctx: Context,
    min_alpha: Annotated[int, typer.Option("--min", help="Minimum alpha value (0-255)", min=0, max=255)] = 1,
    max_alpha: Annotated[int, typer.Option("--max", help="Maximum alpha value (0-255)", min=0, max=255)] = 255,
) -> None:
    """Select pixels by alpha value range."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_by_alpha(min_alpha=min_alpha, max_alpha=max_alpha)
        count = result.get("selected_count", 0)
        _shared._print_result(result, f"Alpha selection: {count} pixels (alpha={min_alpha}-{max_alpha})")


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


@app.command("save-selection")
def save_selection(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Path to save selection mask (PNG)")],
) -> None:
    """Save current selection as a PNG mask image."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.save_selection(path=path)
        _shared._print_result(result, f"Saved selection to {path}")


@app.command("load-selection")
def load_selection(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Path to selection mask (PNG)")],
) -> None:
    """Load selection from a PNG mask image (white=selected, black=unselected)."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.load_selection(path=path)
        _shared._print_result(result, f"Loaded selection from {path}")


@app.command("selection-stats")
def selection_stats(ctx: Context) -> None:
    """Get statistics about current selection (pixel count, centroid, bounding box)."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.selection_stats()
        count = result.get("pixel_count", 0)
        bbox = result.get("bounding_box", {})
        console.print("[green]Selection Statistics:[/green]")
        console.print(f"  Pixel count: [bold]{count}[/bold]")
        if bbox:
            console.print(f"  Bounding box: x={bbox.get('x', '?')}, y={bbox.get('y', '?')}, "
                         f"w={bbox.get('width', '?')}, h={bbox.get('height', '?')}")
        centroid = result.get("centroid", {})
        if centroid:
            console.print(f"  Centroid: ({centroid.get('x', '?')}, {centroid.get('y', '?')})")
        area_pct = result.get("area_percentage")
        if area_pct is not None:
            console.print(f"  Area: {area_pct:.1f}% of canvas")


@app.command("security-status")
def security_status(ctx: Context) -> None:
    """Show current security limits and usage."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.get_security_status()
        rl = result.get("rate_limit", {})
        console.print("[green]Security Status:[/green]")
        console.print(
            f"  Rate limit: [dim]{rl.get('current_usage', 0)}/"
            f"{rl.get('max_commands_per_minute', '?')} per minute[/dim]"
        )
        console.print(
            f"  Payload limit: [dim]"
            f"{result.get('payload_limit', 0) / (1024*1024):.0f}MB[/dim]"
        )
        console.print(
            f"  Batch limit: [dim]"
            f"{result.get('batch_size_limit', '?')} commands[/dim]"
        )
        console.print(
            f"  Max canvas: [dim]"
            f"{result.get('max_canvas_dim', '?')}x"
            f"{result.get('max_canvas_dim', '?')}[/dim]"
        )
        console.print(f"  Max layers: [dim]{result.get('max_layers', '?')}[/dim]")
