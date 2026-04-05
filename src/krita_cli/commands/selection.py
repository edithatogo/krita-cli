import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared

app = typer.Typer()
console = Console()


@app.command("select-area")
def select_area(
    ctx: Context,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    """Select a rectangular area."""
    client = _shared._get_client(ctx)
    with _shared._handle_errors():
        result = client.select_area(x=x, y=y, width=width, height=height)
        _shared._print_result(result, f"Selected area {width}x{height} at ({x}, {y})")


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
