"""Additional integration tests to improve coverage of CLI and MCP error paths."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from krita_cli.cli import app
from krita_client import (
    KritaClient,
    KritaCommandError,
    KritaConnectionError,
    KritaValidationError,
)

runner = CliRunner()


def _mock_client(**kwargs: object) -> KritaClient:
    """Create a KritaClient with all methods mocked."""
    client = KritaClient.__new__(KritaClient)
    client._config = kwargs.get("_config")  # type: ignore[attr-defined]
    for key, value in kwargs.items():
        if key != "_config":
            setattr(client, key, value)
    return client  # type: ignore[return-value]


def test_cli_health_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_get.side_effect = KritaConnectionError("refused")
        result = runner.invoke(app, ["health"])
        assert result.exit_code == 1
        assert "Error:" in result.output


def test_cli_new_canvas_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.new_canvas = lambda **kw: {"error": "failed"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["new-canvas"])
        assert result.exit_code == 1
        assert "Error: failed" in result.output


def test_cli_set_color_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.set_color = lambda **kw: {"error": "bad color"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["set-color", "#ff0000"])
        assert result.exit_code == 1


def test_cli_stroke_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.stroke = lambda **kw: {"error": "no layer"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["stroke", "0,0", "100,100"])
        assert result.exit_code == 1


def test_cli_fill_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.fill = lambda **kw: {"error": "out of bounds"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["fill", "50", "50"])
        assert result.exit_code == 1


def test_cli_draw_shape_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.draw_shape = lambda **kw: {"error": "bad shape"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["draw-shape", "rectangle", "0", "0"])
        assert result.exit_code == 1


def test_cli_get_canvas_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.get_canvas = lambda **kw: {"error": "export failed"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["get-canvas"])
        assert result.exit_code == 1


def test_cli_save_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.save = lambda **kw: {"error": "save failed"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["save", "/tmp/test.png"])
        assert result.exit_code == 1


def test_cli_clear_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.clear = lambda **kw: {"error": "clear failed"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["clear"])
        assert result.exit_code == 1


def test_cli_undo_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.undo = lambda: {"error": "nothing to undo"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["undo"])
        assert result.exit_code == 1


def test_cli_redo_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.redo = lambda: {"error": "nothing to redo"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["redo"])
        assert result.exit_code == 1


def test_cli_get_color_at_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.get_color_at = lambda **kw: {"error": "out of bounds"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["get-color-at", "10", "20"])
        assert result.exit_code == 1


def test_cli_list_brushes_no_results() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.list_brushes = lambda **kw: {"brushes": []}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["list-brushes"])
        assert result.exit_code == 0
        assert "No brushes" in result.output


def test_cli_list_brushes_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.list_brushes = lambda **kw: {"error": "failed", "brushes": None}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["list-brushes"])
        # When brushes is None, get returns None which is falsy → "No brushes" message
        assert result.exit_code == 0
        assert "No brushes" in result.output


def test_cli_open_file_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.open_file = lambda **kw: {"error": "not found"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["open-file", "/tmp/test.kra"])
        assert result.exit_code == 1


def test_cli_call_success() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.send_command = lambda action, params=None: {"status": "ok"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["call", "custom_action", '{"key": "value"}'])
        assert result.exit_code == 0
        assert "ok" in result.output


def test_cli_call_no_params() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.send_command = lambda action, params=None: {"status": "ok"}  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["call", "undo"])
        assert result.exit_code == 0


def test_cli_validation_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.set_color = lambda **kw: (_ for _ in ()).throw(KritaValidationError("bad"))  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["set-color", "invalid"])
        assert result.exit_code == 1


def test_cli_command_error() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = _mock_client()
        mock_client.set_color = lambda **kw: (_ for _ in ()).throw(KritaCommandError("timeout"))  # type: ignore[method-assign]
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["set-color", "#ff0000"])
        assert result.exit_code == 1
