"""Shared CLI utilities used by app.py and command modules."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from typer import Context

from krita_cli import history
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
        self.record: str | None = None


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


def _get_client(ctx: Context) -> KritaClient | _RecordingClient:
    """Create a Krita client from the Typer context."""
    state: CLIState = ctx.obj or CLIState()
    config = ClientConfig()
    if state.url is not None:
        config = ClientConfig(url=state.url)
    client = KritaClient(config)

    # Always wrap in RecordingClient to enable systemic history logging
    return _RecordingClient(client, ctx)


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


# -- Command history integration ----------------------------------------------

_history: list[dict[str, Any]] = []


def _record_command(action: str, params: dict[str, object] | None, result: dict[str, object] | None) -> None:
    """Record a command to the in-memory history and optionally to a file."""
    entry: dict[str, Any] = {
        "action": action,
        "params": params or {},
        "result": result,
    }
    _history.append(entry)


def get_history() -> list[dict[str, Any]]:
    """Return the current command history."""
    return list(_history)


def clear_history() -> None:
    """Clear the in-memory history."""
    _history.clear()


class _RecordingClient:
    """Thin wrapper around KritaClient that records command invocations."""

    def __init__(self, client: KritaClient, ctx: Context) -> None:
        self._client = client
        self._ctx = ctx

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._client, name)
        if not callable(attr):
            return attr

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            action = name
            params = dict(kwargs)
            try:
                result = attr(*args, **kwargs)
                history.record_command(action, params, result)
                return result
            except Exception as exc:
                history.record_command(action, params, {"status": "error", "error": str(exc)})
                raise

        return wrapper


def _maybe_record(
    ctx: Context, action: str, params: dict[str, object] | None, result: dict[str, object] | None
) -> None:
    """Record a command if --record is set on the context."""
    state: CLIState | None = getattr(ctx, "obj", None)
    if state is None:
        return
    record_path = getattr(state, "record", None)
    if record_path is None:
        return

    _record_command(action, params, result)

    if record_path:
        path = Path(record_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_history, indent=2))
