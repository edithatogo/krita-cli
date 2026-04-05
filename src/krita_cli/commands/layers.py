"""Layer-related CLI commands."""

from __future__ import annotations

from typing import Annotated

import typer
from typer import Context

from krita_cli import _shared
from krita_client import KritaError

app = typer.Typer()


@app.command("list")
def list_layers(ctx: Context) -> None:
    """List all layers in the current document."""
    try:
        client = _shared._get_client(ctx)
        result = client.list_layers()
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("create")
def create_layer(
    ctx: Context,
    name: Annotated[str, typer.Option("--name", "-n", help="Layer name")] = "New Layer",
    layer_type: Annotated[str, typer.Option("--type", "-t", help="Layer type")] = "paintlayer",
) -> None:
    """Create a new layer in the current document."""
    try:
        client = _shared._get_client(ctx)
        result = client.create_layer(name=name, layer_type=layer_type)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("select")
def select_layer(
    ctx: Context,
    name: Annotated[str, typer.Argument(help="Layer name to select")],
) -> None:
    """Select a layer by name."""
    try:
        client = _shared._get_client(ctx)
        result = client.select_layer(name=name)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("delete")
def delete_layer(
    ctx: Context,
    name: Annotated[str, typer.Argument(help="Layer name to delete")],
) -> None:
    """Delete a layer by name."""
    try:
        client = _shared._get_client(ctx)
        result = client.delete_layer(name=name)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("rename")
def rename_layer(
    ctx: Context,
    old_name: Annotated[str, typer.Argument(help="Current layer name")],
    new_name: Annotated[str, typer.Argument(help="New layer name")],
) -> None:
    """Rename a layer."""
    try:
        client = _shared._get_client(ctx)
        result = client.rename_layer(old_name=old_name, new_name=new_name)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("set-opacity")
def set_layer_opacity(
    ctx: Context,
    name: Annotated[str, typer.Argument(help="Layer name")],
    opacity: Annotated[float, typer.Option("--opacity", "-o", help="Opacity (0.0 to 1.0)")] = 1.0,
) -> None:
    """Set the opacity of a layer."""
    try:
        client = _shared._get_client(ctx)
        result = client.set_layer_opacity(name=name, opacity=opacity)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)


@app.command("set-visibility")
def set_layer_visibility(
    ctx: Context,
    name: Annotated[str, typer.Argument(help="Layer name")],
    visible: Annotated[bool, typer.Option("--visible/--hidden", "-v/-h", help="Layer visibility")] = True,
) -> None:
    """Toggle the visibility of a layer."""
    try:
        client = _shared._get_client(ctx)
        result = client.set_layer_visibility(name=name, visible=visible)
        _shared._format_result(result)
    except KritaError as exc:
        _shared._handle_error(exc)
