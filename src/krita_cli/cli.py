"""Krita CLI — Command-line interface for programmatic painting in Krita."""

from __future__ import annotations

import json
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from typer import Context

from krita_cli import config_cli
from krita_client import (
    ClientConfig,
    KritaClient,
    KritaCommandError,
    KritaConnectionError,
    KritaError,
    KritaValidationError,
)

app = typer.Typer(
    name="krita",
    help="CLI for programmatic painting in Krita via the MCP plugin.",
    no_args_is_help=True,
    add_completion=False,
)
app.add_typer(config_cli.app, name="config")
console = Console()


class CLIState:
    """Shared state passed through Typer context."""

    def __init__(self) -> None:
        self.url: str | None = None


def _handle_error(exc: KritaError) -> None:
    """Display a Krita client error and exit."""
    console.print(f"[red]Error:[/red] {exc.message}")
    if exc.code:
        console.print(f"[dim]Code: {exc.code}[/dim]")

    if getattr(exc, "recoverable", False):
        if exc.code == "NO_ACTIVE_DOCUMENT":
            console.print("[green]Hint: Open a document or create a new canvas first.[/green]")
        elif exc.code == "INVALID_PARAMS":
            console.print("[green]Hint: Check your input values are within allowed ranges.[/green]")
        elif exc.code == "LAYER_NOT_FOUND":
            console.print("[green]Hint: Ensure there is an active paint layer in your document.[/green]")
        else:
            console.print("[green]Hint: This error appears to be recoverable. Adjust your request and try again.[/green]")

    raise typer.Exit(code=1)


def _get_client(ctx: Context) -> KritaClient:
    """Create a Krita client from the Typer context."""
    state: CLIState = ctx.obj or CLIState()
    config = ClientConfig()
    if state.url is not None:
        config = ClientConfig(url=state.url)
    return KritaClient(config)


def _format_result(result: dict[str, object]) -> None:
    """Display a command result in a readable format."""
    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        raise typer.Exit(code=1)
    for key, value in result.items():  # pragma: no cover - display-only
        if key == "status":
            continue
        console.print(f"[dim]{key}:[/dim] {value}")


# -- Global options -----------------------------------------------------------


@app.callback()
def callback(
    ctx: Context,
    url: Annotated[
        str | None,
        typer.Option("--url", "-u", help="Krita plugin URL (overrides KRITA_URL env var)"),
    ] = None,
) -> None:
    """Krita CLI — programmatic painting in Krita."""
    ctx.obj = CLIState()
    ctx.obj.url = url


# -- Health -------------------------------------------------------------------


@app.command()
def health(ctx: Context) -> None:
    """Check if Krita is running with the MCP plugin active."""
    try:
        client = _get_client(ctx)
        result = client.health()
        plugin = result.get("plugin", "unknown")
        status = result.get("status", "unknown")
        console.print(f"[green]Krita is running.[/green] Plugin: [bold]{plugin}[/bold] ({status})")
    except KritaError as exc:
        _handle_error(exc)


# -- Canvas operations --------------------------------------------------------


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
        client = _get_client(ctx)
        result = client.new_canvas(width=width, height=height, name=name, background=background)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command("set-color")
def set_color(
    ctx: Context,
    color: Annotated[str, typer.Argument(help="Hex color code (e.g., #ff6b6b)")],
) -> None:
    """Set the foreground paint color."""
    try:
        client = _get_client(ctx)
        result = client.set_color(color=color)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command("set-brush")
def set_brush(
    ctx: Context,
    preset: Annotated[str | None, typer.Option("--preset", "-p", help="Brush preset name")] = None,
    size: Annotated[int | None, typer.Option("--size", "-s", help="Brush size in pixels")] = None,
    opacity: Annotated[float | None, typer.Option("--opacity", "-o", help="Brush opacity (0.0-1.0)")] = None,
) -> None:
    """Set brush preset and properties."""
    try:
        client = _get_client(ctx)
        result = client.set_brush(preset=preset, size=size, opacity=opacity)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


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
        client = _get_client(ctx)
        result = client.stroke(
            points=parsed_points,
            pressure=pressure,
            size=size,
            hardness=hardness,
            opacity=opacity,
        )
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command()
def fill(
    ctx: Context,
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
    radius: Annotated[int, typer.Option("--radius", "-r", help="Fill radius in pixels")] = 50,
) -> None:
    """Fill a circular area with the current color."""
    try:
        client = _get_client(ctx)
        result = client.fill(x=x, y=y, radius=radius)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


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
        client = _get_client(ctx)
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
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command("get-canvas")
def get_canvas(
    ctx: Context,
    filename: Annotated[str, typer.Option("--filename", "-f", help="Output filename")] = "canvas.png",
) -> None:
    """Export the current canvas to a PNG file."""
    console.print("[dim]Exporting canvas (this may take a while for large canvases)...[/dim]")
    try:
        client = _get_client(ctx)
        result = client.get_canvas(filename=filename)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command()
def save(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Full file path to save to")],
) -> None:
    """Save the current canvas to a specific file path."""
    console.print("[dim]Saving canvas (this may take a while for large canvases)...[/dim]")
    try:
        client = _get_client(ctx)
        result = client.save(path=path)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command()
def clear(
    ctx: Context,
    color: Annotated[str, typer.Option("--color", "-c", help="Color to fill with")] = "#1a1a2e",
) -> None:
    """Clear the canvas to a solid color."""
    try:
        client = _get_client(ctx)
        result = client.clear(color=color)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


# -- Navigation ---------------------------------------------------------------


@app.command()
def undo(ctx: Context) -> None:
    """Undo the last action."""
    try:
        client = _get_client(ctx)
        result = client.undo()
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command()
def redo(ctx: Context) -> None:
    """Redo the last undone action."""
    try:
        client = _get_client(ctx)
        result = client.redo()
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


# -- Query operations ---------------------------------------------------------


@app.command("get-color-at")
def get_color_at(
    ctx: Context,
    x: Annotated[int, typer.Argument(help="X coordinate")],
    y: Annotated[int, typer.Argument(help="Y coordinate")],
) -> None:
    """Sample the color at a specific pixel (eyedropper)."""
    try:
        client = _get_client(ctx)
        result = client.get_color_at(x=x, y=y)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


@app.command("list-brushes")
def list_brushes(
    ctx: Context,
    filter: Annotated[str, typer.Option("--filter", "-f", help="Filter by name")] = "",  # noqa: A002
    limit: Annotated[int, typer.Option("--limit", "-l", help="Maximum number to return")] = 20,
) -> None:
    """List available brush presets."""
    try:
        client = _get_client(ctx)
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
        _handle_error(exc)


@app.command("open-file")
def open_file(
    ctx: Context,
    path: Annotated[str, typer.Argument(help="Full file path to open")],
) -> None:
    """Open an existing file in Krita (.kra, .png, .jpg, etc)."""
    try:
        client = _get_client(ctx)
        result = client.open_file(path=path)
        _format_result(result)
    except KritaError as exc:
        _handle_error(exc)


# -- Raw command mode ---------------------------------------------------------


@app.command()
def call(
    ctx: Context,
    action: Annotated[str, typer.Argument(help="Command action name")],
    params_json: Annotated[str | None, typer.Argument(help="JSON params string")] = None,
) -> None:
    """Send a raw command to the Krita plugin.

    Useful for commands not yet exposed as subcommands, or for scripting.

    \b
    Examples:
        krita call new-canvas '{"width": 1920, "height": 1080}'
        krita call set-color '{"color": "#ff0000"}'
        krita call stroke '{"points": [[0,0],[100,100]]}'
    """
    params: dict[str, object] = {}
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as exc:
            console.print(f"[red]Error:[/red] Invalid JSON: {exc}")
            raise typer.Exit(code=1) from exc

    try:
        client = _get_client(ctx)
        result = client.send_command(action, params)
        console.print(json.dumps(result, indent=2, default=str))
    except KritaError as exc:
        _handle_error(exc)


# -- Entry point --------------------------------------------------------------


def main() -> None:  # pragma: no cover
    """Main entry point for the CLI."""
    try:
        app()
    except (KritaConnectionError, KritaCommandError, KritaValidationError) as exc:
        _handle_error(exc)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/dim]")
        sys.exit(130)


if __name__ == "__main__":  # pragma: no cover
    main()
