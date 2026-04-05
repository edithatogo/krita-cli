"""Command history CLI commands: history, replay."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from typer import Context

from krita_cli import _shared
from krita_cli.history import (
    clear_history,
    get_history,
    get_system_log_path,
    is_recording,
    load_history,
    replay_commands,
    rollback_batch,
)

console = Console()

app = typer.Typer()


@app.command("log")
def log(
    ctx: Context,
    file: Annotated[
        str | None,
        typer.Option("--file", "-f", help="Load history from a JSON file instead of in-memory"),
    ] = None,
    limit: Annotated[
        int | None,
        typer.Option("--limit", "-l", help="Show only the last N entries"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output as JSON"),
    ] = False,
) -> None:
    """Show command history."""
    if file:
        entries = load_history(file)
    else:
        entries = get_history()
        if not entries:
            # Fallback to system log if in-memory is empty
            entries = load_history(get_system_log_path())

    if limit:
        entries = entries[-limit:]

    if json_output:
        console.print(json.dumps(entries, indent=2))
        return

    if not entries:
        console.print("[dim]No commands in history.[/dim]")
        return

    table = Table(title="Command History")
    table.add_column("#", style="dim")
    table.add_column("Action")
    table.add_column("Params")
    table.add_column("Status", style="dim")

    for i, entry in enumerate(entries, 1):
        action = entry.get("action", "unknown")
        params = entry.get("params", {})
        result = entry.get("result", {})
        status = result.get("status", "?") if isinstance(result, dict) else "?"
        params_str = str(params) if params else "-"
        if len(params_str) > 40:
            params_str = params_str[:37] + "..."
        table.add_row(str(i), action, params_str, status)

    console.print(table)

    if is_recording():
        console.print("\n[dim]Recording is enabled.[/dim]")


@app.command()
def replay(
    ctx: Context,
    file: Annotated[
        str | None,
        typer.Option("--file", "-f", help="Replay commands from a JSON file"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be replayed without executing"),
    ] = False,
) -> None:
    """Replay recorded commands."""
    if file:
        entries = load_history(file)
    else:
        entries = get_history()
        if not entries:
            entries = load_history(get_system_log_path())

    if not entries:
        console.print("[dim]No commands to replay.[/dim]")
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"Would replay {len(entries)} command(s):")
        for i, entry in enumerate(entries, 1):
            action = entry.get("action", "unknown")
            params = entry.get("params", {})
            console.print(f"  {i}. {action}({params})")
        return

    console.print(f"Replaying {len(entries)} command(s)...")
    try:
        client = _shared._get_client(ctx)
        results = replay_commands(  # type: ignore[arg-type]
            file_path=file,
            client=client,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        )
    except Exception as exc:
        console.print(f"[red]Replay failed: {exc}[/red]")
        raise typer.Exit(code=1) from exc

    success = sum(1 for r in results if r["status"] == "ok")
    failed = len(results) - success

    for i, result in enumerate(results, 1):
        action = result["action"]
        status = result["status"]
        if status == "ok":
            console.print(f"  [green]{i}. {action} - OK[/green]")
        else:
            error = result.get("error", "unknown")
            console.print(f"  [red]{i}. {action} - FAILED: {error}[/red]")

    console.print(f"\n[dim]Results: {success} succeeded, {failed} failed[/dim]")

    if failed > 0:
        raise typer.Exit(code=1)


@app.command("clear")
def clear_cmd() -> None:
    """Clear the in-memory command history."""
    clear_history()
    console.print("[dim]Command history cleared.[/dim]")


@app.command()
def rollback(
    ctx: Context,
    count: Annotated[int, typer.Option("--count", "-c", help="Number of steps to rollback")] = 1,
) -> None:
    """Rollback the last N operations by calling undo."""
    if count < 1:
        console.print("[red]Error:[/red] Count must be at least 1.")
        raise typer.Exit(code=1)

    console.print(f"Rolling back [bold]{count}[/bold] operation(s)...")
    try:
        client = _shared._get_client(ctx)
        results = rollback_batch(count=count, client=client)  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]

        success = sum(1 for r in results if r["status"] == "ok")
        for res in results:
            if res["status"] == "ok":
                console.print(f"  [green]Step {res['iteration']}: OK[/green]")
            else:
                console.print(f"  [red]Step {res['iteration']}: FAILED ({res['error']})[/red]")

        console.print(f"\n[dim]Rollback complete: {success}/{count} succeeded[/dim]")
    except Exception as exc:
        console.print(f"[red]Error:[/red] Rollback failed: {exc}")
        raise typer.Exit(code=1) from exc
