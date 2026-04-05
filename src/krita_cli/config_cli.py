"""Krita CLI — Plugin configuration management."""

from __future__ import annotations

import json
import os
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="config",
    help="Manage Krita MCP plugin configuration.",
    no_args_is_help=True,
)
console = Console()

CONFIG_PATH = os.path.expanduser("~/.kritamcp_config.json")


def _read_config() -> dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Error reading config:[/red] {e}")
        return {}


def _write_config(config: dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        console.print(f"[red]Error writing config:[/red] {e}")


@app.command("show")
def show_config() -> None:
    """Show the current plugin configuration."""
    config = _read_config()

    table = Table(title=f"Plugin Config (reads from {CONFIG_PATH})")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    if not config:
        table.add_row("(No config stored)", "(default values will be used)")
    else:
        for k, v in config.items():
            table.add_row(str(k), str(v))

    console.print(table)


@app.command("set")
def set_config(
    key: Annotated[str, typer.Argument(help="Configuration key (e.g., port, output_dir, max_canvas_dim)")],
    value: Annotated[str, typer.Argument(help="Configuration value")],
) -> None:
    """Set a plugin configuration value.

    Common keys:
    - port: e.g., 5678
    - output_dir: e.g., ~/krita-mcp-output
    - max_canvas_dim: e.g., 8192

    Changes require restarting Krita to take effect.
    """
    config = _read_config()

    # Try typing parsing
    parsed_val: Any = value
    if value.isdigit():
        parsed_val = int(value)
    elif value.lower() in ["true", "false"]:
        parsed_val = value.lower() == "true"

    config[key] = parsed_val
    _write_config(config)

    console.print(f"[green]Successfully set [bold]{key}[/bold] = {parsed_val}[/green]")
    console.print("[dim]Note: You must restart Krita or reload the plugin for changes to take effect.[/dim]")
