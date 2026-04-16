"""History command CLI subcommand."""

from __future__ import annotations

import json
from typing import Annotated, Any, cast

import typer
from rich.console import Console
from rich.table import Table
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

console = Console()

app = typer.Typer()


@app.command()
def history(
    ctx: Context,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of history entries to show")] = 20,
    as_json: Annotated[bool, typer.Option("--json", "-j", help="Output as raw JSON")] = False,  # noqa: FBT002
) -> None:
    """View recent command execution history."""
    try:
        client = _shared._get_client(ctx)
        result = client.get_command_history(limit=limit)

        if as_json:
            console.print(json.dumps(result, indent=2, default=str))
            return

        records_raw = result.get("history", [])
        if not isinstance(records_raw, list):
            records_raw = []
        records = cast("list[dict[str, Any]]", records_raw)

        if not records:
            console.print("[dim]No command history recorded.[/dim]")
            return

        table = Table(title=f"Command History ({len(records)} entries)")
        table.add_column("#", style="dim")
        table.add_column("Action")
        table.add_column("Status")
        table.add_column("Duration (ms)")
        table.add_column("Error", style="red")

        for i, rec in enumerate(records, 1):
            table.add_row(
                str(i),
                rec.get("action", "?"),
                rec.get("status", "?"),
                f"{rec.get('duration_ms', 0):.1f}",
                rec.get("error", "") or "",
            )

        console.print(table)

    except KritaError as exc:
        _shared._handle_error(exc)
