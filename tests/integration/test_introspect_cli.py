"""Integration tests for introspection CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app
from krita_client import KritaError

runner = CliRunner()


@pytest.fixture
def mock_client():
    with patch("krita_cli._shared._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_canvas_info(mock_client) -> None:
    mock_client.get_canvas_info.return_value = {"status": "ok", "width": 800, "height": 600}
    result = runner.invoke(app, ["introspect", "canvas-info"])
    assert result.exit_code == 0
    assert "width" in result.stdout


def test_current_color(mock_client) -> None:
    mock_client.get_current_color.return_value = {"status": "ok", "foreground": "#ff0000"}
    result = runner.invoke(app, ["introspect", "current-color"])
    assert result.exit_code == 0
    assert "#ff0000" in result.stdout


def test_current_brush(mock_client) -> None:
    mock_client.get_current_brush.return_value = {"status": "ok", "preset": "Soft"}
    result = runner.invoke(app, ["introspect", "current-brush"])
    assert result.exit_code == 0
    assert "Soft" in result.stdout


def test_canvas_info_error(mock_client) -> None:
    mock_client.get_canvas_info.side_effect = KritaError("failed")
    result = runner.invoke(app, ["introspect", "canvas-info"])
    assert result.exit_code == 1


def test_current_color_error(mock_client) -> None:
    mock_client.get_current_color.side_effect = KritaError("failed")
    result = runner.invoke(app, ["introspect", "current-color"])
    assert result.exit_code == 1


def test_current_brush_error(mock_client) -> None:
    mock_client.get_current_brush.side_effect = KritaError("failed")
    result = runner.invoke(app, ["introspect", "current-brush"])
    assert result.exit_code == 1
