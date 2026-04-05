"""Raw command mode CLI command: call."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


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
        client = _shared._get_client(ctx)
        result = client.send_command(action, params)
        console.print(json.dumps(result, indent=2, default=str))
    except KritaError as exc:
        _shared._handle_error(exc)
