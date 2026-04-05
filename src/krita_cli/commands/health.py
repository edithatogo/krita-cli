"""Health check CLI command."""

from __future__ import annotations

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command()
def health(ctx: Context) -> None:
    """Check if Krita is running with the MCP plugin active."""
    try:
        client = _shared._get_client(ctx)
        result = client.health()
        plugin = result.get("plugin", "unknown")
        status = result.get("status", "unknown")
        version = result.get("version", "unknown")
        protocol_version = result.get("protocol_version", "unknown")
        console.print(
            f"[green]Krita is running.[/green] Plugin: [bold]{plugin}[/bold] "
            f"v{version} (protocol v{protocol_version}, {status})"
        )
    except KritaError as exc:
        _shared._handle_error(exc)
