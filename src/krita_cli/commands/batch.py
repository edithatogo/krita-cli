"""Batch command CLI command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command()
def batch(
    ctx: Context,
    file: Annotated[Path, typer.Argument(help="JSON file with batch commands")],
    stop_on_error: Annotated[bool, typer.Option("--stop-on-error", help="Stop on first error")] = False,
) -> None:
    """Execute multiple commands from a JSON file.

    The JSON file should contain an array of command objects, each with
    an "action" and optional "params" key.

    Example JSON file:
    [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
        {"action": "fill", "params": {"x": 200, "y": 200, "radius": 30}}
    ]
    """
    try:
        commands = json.loads(file.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[red]Error:[/red] Invalid JSON in {file}: {exc}")
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        console.print(f"[red]Error:[/red] Cannot read {file}: {exc}")
        raise typer.Exit(code=1) from exc

    if not isinstance(commands, list):
        console.print("[red]Error:[/red] JSON file must contain an array of commands.")
        raise typer.Exit(code=1)

    try:
        client = _shared._get_client(ctx)
        result = client.batch_execute(commands, stop_on_error=stop_on_error)
        status = result.get("status", "unknown")
        results_raw = result.get("results", [])
        if not isinstance(results_raw, list):
            results_raw = []
        results = cast("list[dict[str, Any]]", results_raw)

        ok = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "ok")
        errs = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "error")
        count = result.get("count", 0)
        color = "green" if status == "ok" else "red" if status == "error" else "yellow"
        console.print(f"[{color}]Batch: {status}[/{color}]")
        console.print(f"  {ok} succeeded, {errs} failed out of {count}")
        batch_id = result.get("batch_id")
        if batch_id:
            console.print(f"  Batch ID: [dim]{batch_id}[/dim]")
        if errs > 0:
            console.print("[red]Errors:[/red]")
            for r in results:
                if isinstance(r, dict) and r.get("status") == "error":
                    err_msg = r.get("error")
                    if not err_msg:
                        result_data = r.get("result", {})
                        if isinstance(result_data, dict) and "error" in result_data:
                            err_info = result_data["error"]
                            err_msg = (
                                err_info.get("message", str(err_info)) if isinstance(err_info, dict) else str(err_info)
                            )
                    if not err_msg:
                        err_msg = "unknown"
                    console.print(f"  [red]✗ {r.get('action', 'unknown')}: {err_msg}[/red]")
    except KritaError as exc:
        _shared._handle_error(exc)
