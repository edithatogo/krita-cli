"""Tests for CLI error paths in individual commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from krita_cli.cli import app
from krita_client import KritaError

runner = CliRunner()


def _mock_error_client() -> MagicMock:
    mock = MagicMock()
    for method in [
        "new_canvas",
        "set_color",
        "set_brush",
        "stroke",
        "fill",
        "draw_shape",
        "get_canvas",
        "save",
        "clear",
        "undo",
        "redo",
        "get_color_at",
        "list_brushes",
        "open_file",
    ]:
        setattr(mock, method, lambda **kw: (_ for _ in ()).throw(KritaError("cmd failed")))
    mock.list_brushes = lambda **kw: (_ for _ in ()).throw(KritaError("cmd failed"))
    return mock


def test_cli_new_canvas_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["new-canvas"])
        assert result.exit_code == 1


def test_cli_set_color_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["set-color", "#ff0000"])
        assert result.exit_code == 1


def test_cli_set_brush_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["set-brush"])
        assert result.exit_code == 1


def test_cli_stroke_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["stroke", "0,0", "100,100"])
        assert result.exit_code == 1


def test_cli_fill_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["fill", "50", "50"])
        assert result.exit_code == 1


def test_cli_draw_shape_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["draw-shape", "rectangle", "0", "0"])
        assert result.exit_code == 1


def test_cli_get_canvas_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["get-canvas"])
        assert result.exit_code == 1


def test_cli_save_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["save", "/tmp/test.png"])
        assert result.exit_code == 1


def test_cli_clear_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["clear"])
        assert result.exit_code == 1


def test_cli_undo_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["undo"])
        assert result.exit_code == 1


def test_cli_redo_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["redo"])
        assert result.exit_code == 1


def test_cli_get_color_at_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["get-color-at", "10", "20"])
        assert result.exit_code == 1


def test_cli_list_brushes_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["list-brushes"])
        assert result.exit_code == 1


def test_cli_open_file_error_path() -> None:
    with patch("krita_cli.cli._get_client") as mock_get:
        mock_get.return_value = _mock_error_client()
        result = runner.invoke(app, ["open-file", "/tmp/test.kra"])
        assert result.exit_code == 1
