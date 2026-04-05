"""CLI commands for plugin configuration: show, set, reset."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from krita_cli import config_cmd

app = typer.Typer(name="config", help="Plugin configuration commands.")
console = Console()


@app.command("show")
def config_show() -> None:
    """Show current plugin configuration."""
    config = config_cmd.load_config()
    table = Table(title=f"Plugin Config ({config_cmd.CONFIG_FILE})")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for key, value in config.items():
        table.add_row(str(key), str(value))
    console.print(table)


@app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Configuration key")],
    value: Annotated[str, typer.Argument(help="Configuration value")],
) -> None:
    """Set a plugin configuration value."""
    try:
        config_cmd.set_key(key, value)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]Set {key} = {value}[/green]")
    console.print("[dim]Restart Krita for changes to take effect.[/dim]")


@app.command("reset")
def config_reset() -> None:
    """Reset plugin configuration to defaults."""
    config_cmd.reset_config()
    console.print("[green]Configuration reset to defaults.[/green]")
