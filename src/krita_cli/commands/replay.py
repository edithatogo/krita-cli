"""Replay command CLI subcommand."""

from __future__ import annotations

import json
import pathlib
import time
from typing import Annotated

import typer
from rich.console import Console
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


def _validate_records(records: list[dict]) -> None:
    """Validate that all records have required 'action' field."""
    for i, rec in enumerate(records, 1):
        action = rec.get("action")
        if not action:
            console.print(f"  [red]#{i}: Missing 'action' field[/red]")
            raise typer.Exit(code=1)


def _execute_replay(
    ctx: Context,
    records: list[dict],
    speed: float,
) -> None:
    """Execute recorded commands via the client."""
    client = _shared._get_client(ctx)
    ok_count = 0
    err_count = 0

    for i, rec in enumerate(records, 1):
        action = rec.get("action")
        params = rec.get("params", {})

        if not action:
            console.print(f"  [red]#{i}: Skipping — missing 'action'[/red]")
            err_count += 1
            continue

        if speed > 0:
            original_ms = rec.get("duration_ms", 0) / 1000.0
            delay = original_ms / speed
            if delay > 0:
                time.sleep(delay)

        try:
            result = client.send_command(action, params)
            if "error" in result:
                err_msg = result.get("error", {})
                if isinstance(err_msg, dict):
                    err_msg = err_msg.get("message", str(err_msg))
                console.print(f"  [red]#{i}: {action} — {err_msg}[/red]")
                err_count += 1
            else:
                ok_count += 1
        except KritaError as exc:
            console.print(f"  [red]#{i}: {action} — {exc}[/red]")
            err_count += 1

    console.print(
        f"\nReplay complete: {ok_count} succeeded,"
        f" {err_count} failed out of {len(records)}"
    )


@app.command()
def replay(
    ctx: Context,
    file: Annotated[
        str,
        typer.Argument(help="JSON file with recorded commands"),
    ],
    speed: Annotated[
        float,
        typer.Option("--speed", "-s", help="Playback speed (0.0=instant, 1.0=original)"),
    ] = 1.0,
    dry_run: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--dry-run", "-n", help="Validate without executing"),
    ] = False,
) -> None:
    """Replay commands from a JSON file.

    The JSON file should contain an array of command records from
    'krita history --json', each with an "action" and optional "params" key.

    Example:
        krita history --json > history.json
        krita replay history.json
        krita replay history.json --speed 0.5
        krita replay history.json --dry-run
    """
    path = pathlib.Path(file)
    try:
        records = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[red]Error:[/red] Invalid JSON in {path}: {exc}")
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        console.print(f"[red]Error:[/red] Cannot read {path}: {exc}")
        raise typer.Exit(code=1) from exc

    if not isinstance(records, list):
        console.print("[red]Error:[/red] JSON file must contain an array.")
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[dim]Dry run: validating {len(records)} records[/dim]")
        _validate_records(records)
        console.print(f"[green]All {len(records)} records are valid.[/green]")
        return

    try:
        _execute_replay(ctx, records, speed)
    except KritaError as exc:
        _shared._handle_error(exc)
