"""Integration tests for krita_cli."""

from __future__ import annotations

from typer.testing import CliRunner

from krita_cli.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CLI for programmatic painting" in result.output


def test_cli_no_args_shows_help() -> None:
    result = runner.invoke(app)
    # Typer exits with code 2 when no command given and no_args_is_help=True
    assert result.exit_code in (0, 2)
    assert "Commands" in result.output


def test_cli_health_connection_error() -> None:
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 1
    assert "Cannot connect to Krita" in result.output


def test_cli_stroke_invalid_point_format() -> None:
    result = runner.invoke(app, ["stroke", "stroke", "invalid"])
    assert result.exit_code == 1
    assert "Invalid point format" in result.output


def test_cli_call_invalid_json() -> None:
    result = runner.invoke(app, ["call", "test", "not-json"])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.output


def test_cli_list_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert "canvas" in result.output
    assert "color" in result.output
    assert "stroke" in result.output
    assert "health" in result.output
    assert "call" in result.output
    assert "selection" in result.output
    assert "batch" in result.output
