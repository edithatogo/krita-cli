"""Shared CLI utilities used by app.py and command modules."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

import typer
from rich.console import Console
from typer import Context

from krita_client import (
    ClientConfig,
    ErrorCode,
    KritaClient,
    KritaError,
)

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

    if exc.recoverable:
        if exc.code == ErrorCode.NO_ACTIVE_DOCUMENT:
            console.print("[green]Hint: Open a document or create a new canvas first.[/green]")
        elif exc.code == ErrorCode.INVALID_PARAMETERS:
            console.print("[green]Hint: Check your input values are within allowed ranges.[/green]")
        elif exc.code == ErrorCode.LAYER_NOT_FOUND:
            console.print("[green]Hint: Ensure there is an active paint layer in your document.[/green]")
        elif exc.code == ErrorCode.PLUGIN_UNREACHABLE:
            console.print("[green]Hint: Make sure Krita is running with the MCP plugin enabled.[/green]")
        elif exc.code == ErrorCode.COMMAND_TIMEOUT:
            console.print("[green]Hint: The operation took too long. Try again or check Krita status.[/green]")
        elif exc.code == ErrorCode.BRUSH_NOT_FOUND:
            console.print("[green]Hint: Check the brush preset name or list available brushes first.[/green]")
        elif exc.code == ErrorCode.FILE_NOT_FOUND:
            console.print("[green]Hint: Verify the file path exists and is accessible.[/green]")
        else:
            console.print(
                "[green]Hint: This error appears to be recoverable. Adjust your request and try again.[/green]"
            )

    raise typer.Exit(code=1)


@contextmanager
def _handle_errors() -> Any:
    """Context manager to handle Krita errors gracefully."""
    try:
        yield
    except KritaError as exc:
        _handle_error(exc)


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


def _print_result(result: dict[str, object], message: str) -> None:
    """Display a command result with a custom message."""
    console.print(f"[green]{message}[/green]")
    _format_result(result)
