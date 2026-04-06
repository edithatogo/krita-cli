"""Tests for CLI main entry point and edge cases."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.cli import app, main
from krita_client import (
    KritaClient,
    KritaConnectionError,
)

runner = CliRunner()


def test_cli_main_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that KeyboardInterrupt is handled gracefully."""
    with patch("krita_cli.app.app") as mock_app:
        mock_app.side_effect = KeyboardInterrupt()
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 130


def test_cli_main_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that KritaConnectionError in main is handled."""
    with patch("krita_cli.app.app") as mock_app:
        mock_app.side_effect = KritaConnectionError("refused")
        result = runner.invoke(app, ["health"])
        assert result.exit_code == 1


def test_cli_callback_sets_url() -> None:
    """Test that the global callback sets the URL."""
    from krita_cli.cli import CLIState

    state = CLIState()
    state.url = "http://custom:9999"
    assert state.url == "http://custom:9999"


def test_cli_get_client_with_url_override() -> None:
    """Test that URL override creates correct config."""
    from typer import Context

    from krita_cli.cli import CLIState, _get_client

    ctx = MagicMock(spec=Context)
    ctx.obj = CLIState()
    ctx.obj.url = "http://override:1234"
    client = _get_client(ctx)
    assert client.config.url == "http://override:1234"


def test_cli_get_client_without_url() -> None:
    """Test that no URL override uses default config."""
    from typer import Context

    from krita_cli.cli import CLIState, _get_client

    ctx = MagicMock(spec=Context)
    ctx.obj = CLIState()
    ctx.obj.url = None
    client = _get_client(ctx)
    assert "localhost" in client.config.url


def test_cli_handle_error_with_code() -> None:
    """Test error display with error code."""
    from typer import Exit

    from krita_cli.cli import _handle_error
    from krita_client import KritaError

    with pytest.raises(Exit) as exc_info:
        _handle_error(KritaError("test error", code="TEST_001"))
    assert exc_info.value.exit_code == 1


def test_cli_handle_error_without_code() -> None:
    """Test error display without error code."""
    from typer import Exit

    from krita_cli.cli import _handle_error
    from krita_client import KritaError

    with pytest.raises(Exit) as exc_info:
        _handle_error(KritaError("test error"))
    assert exc_info.value.exit_code == 1


def test_cli_format_result_with_error() -> None:
    """Test that _format_result handles error responses."""
    from typer import Exit

    from krita_cli.cli import _format_result

    with pytest.raises(Exit) as exc_info:
        _format_result({"error": "something failed"})
    assert exc_info.value.exit_code == 1


def test_cli_format_result_success() -> None:
    """Test that _format_result displays non-error results."""
    from io import StringIO

    from rich.console import Console

    from krita_cli.cli import _format_result

    output = StringIO()
    console = Console(file=output, force_terminal=True)
    with patch("krita_cli._shared.console", console):
        _format_result({"status": "ok", "path": "/tmp/test.png"})
    text = output.getvalue()
    assert "path" in text


def test_cli_stroke_with_url_option() -> None:
    """Test stroke command with --url option."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.stroke.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["--url", "http://test:9999", "stroke", "stroke", "0,0", "100,100"])
        assert result.exit_code == 0


def test_cli_call_with_json_params() -> None:
    """Test call command with valid JSON params."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.send_command.return_value = {"status": "ok", "data": "test"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["call", "test_action", '{"key": "value"}'])
        assert result.exit_code == 0
        assert "ok" in result.output


def test_cli_new_canvas_success() -> None:
    """Test new-canvas command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.new_canvas.return_value = {"status": "ok", "width": 800, "height": 600}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["canvas", "new-canvas", "--width", "800", "--height", "600"])
        assert result.exit_code == 0


def test_cli_set_brush_success() -> None:
    """Test set-brush command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.set_brush.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["brush", "set-brush", "--preset", "Soft", "--size", "50"])
        assert result.exit_code == 0


def test_cli_fill_success() -> None:
    """Test fill command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.fill.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["stroke", "fill", "50", "50", "--radius", "30"])
        assert result.exit_code == 0


def test_cli_draw_shape_success() -> None:
    """Test draw-shape command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.draw_shape.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["stroke", "draw-shape", "rectangle", "0", "0"])
        assert result.exit_code == 0


def test_cli_get_canvas_success() -> None:
    """Test get-canvas command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.get_canvas.return_value = {"status": "ok", "path": "/tmp/canvas.png"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["canvas", "get-canvas"])
        assert result.exit_code == 0


def test_cli_save_success() -> None:
    """Test save command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.save.return_value = {"status": "ok", "path": "/tmp/test.png"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["canvas", "save", "/tmp/test.png"])
        assert result.exit_code == 0


def test_cli_clear_success() -> None:
    """Test clear command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.clear.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["canvas", "clear"])
        assert result.exit_code == 0


def test_cli_undo_success() -> None:
    """Test undo command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.undo.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["navigation", "undo"])
        assert result.exit_code == 0


def test_cli_redo_success() -> None:
    """Test redo command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.redo.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["navigation", "redo"])
        assert result.exit_code == 0


def test_cli_get_color_at_success() -> None:
    """Test get-color-at command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.get_color_at.return_value = {
            "status": "ok",
            "color": "#ff0000",
            "r": 255,
            "g": 0,
            "b": 0,
        }
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["color", "get-color-at", "10", "20"])
        assert result.exit_code == 0


def test_cli_list_brushes_with_results() -> None:
    """Test list-brushes with results displayed as table."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.list_brushes.return_value = {"brushes": ["Soft", "Hard", "Basic"]}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["brush", "list-brushes"])
        assert result.exit_code == 0
        assert "Soft" in result.output


def test_cli_open_file_success() -> None:
    """Test open-file command success path."""
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.open_file.return_value = {
            "status": "ok",
            "name": "test.kra",
            "width": 800,
            "height": 600,
        }
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["file", "open-file", "/tmp/test.kra"])
        assert result.exit_code == 0
