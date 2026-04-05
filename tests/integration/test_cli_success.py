"""Tests for CLI success paths to reach 100% coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from krita_cli.cli import app

runner = CliRunner()


def test_cli_health_success() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.health.return_value = {"status": "ok", "plugin": "kritamcp"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["health"])
        assert result.exit_code == 0
        assert "kritamcp" in result.output


def test_cli_new_canvas_with_all_options() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.new_canvas.return_value = {"status": "ok", "width": 1920, "height": 1080, "name": "Test"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["new-canvas", "-W", "1920", "-H", "1080", "-n", "Test", "-b", "#000000"])
        assert result.exit_code == 0
        assert "1920" in result.output


def test_cli_set_brush_with_opacity() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_brush.return_value = {"status": "ok", "preset": "Soft", "size": 50}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["set-brush", "-p", "Soft", "-s", "50", "-o", "0.8"])
        assert result.exit_code == 0
        assert "Soft" in result.output


def test_cli_stroke_with_all_options() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.stroke.return_value = {"status": "ok", "points_count": 2}
        mock_get.return_value = mock_client
        result = runner.invoke(
            app,
            ["stroke", "0,0", "100,100", "--pressure", "0.5", "-s", "30", "--hardness", "0.3", "-o", "0.7"],
        )
        assert result.exit_code == 0


def test_cli_fill_with_radius() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.fill.return_value = {"status": "ok", "x": 50, "y": 50, "radius": 100}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["fill", "50", "50", "-r", "100"])
        assert result.exit_code == 0


def test_cli_draw_shape_with_all_options() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.draw_shape.return_value = {"status": "ok", "shape": "line"}
        mock_get.return_value = mock_client
        result = runner.invoke(
            app,
            ["draw-shape", "line", "0", "0", "--x2", "100", "--y2", "100", "--no-fill", "--stroke"],
        )
        assert result.exit_code == 0


def test_cli_get_canvas_with_filename() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_canvas.return_value = {"status": "ok", "path": "/tmp/custom.png"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["get-canvas", "-f", "custom.png"])
        assert result.exit_code == 0
        assert "custom.png" in result.output


def test_cli_clear_with_color() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.clear.return_value = {"status": "ok", "color": "#ffffff"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["clear", "-c", "#ffffff"])
        assert result.exit_code == 0


def test_cli_list_brushes_with_filter() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.list_brushes.return_value = {"brushes": ["Soft Round"], "count": 1}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["list-brushes", "-f", "soft", "-l", "5"])
        assert result.exit_code == 0
        assert "Soft Round" in result.output


def test_cli_save_with_result() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.save.return_value = {"status": "ok", "path": "/tmp/test.png"}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["save", "/tmp/test.png"])
        assert result.exit_code == 0


def test_cli_get_color_at_with_result() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_color_at.return_value = {"status": "ok", "color": "#ff0000", "r": 255, "g": 0, "b": 0}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["get-color-at", "10", "20"])
        assert result.exit_code == 0
        assert "#ff0000" in result.output


def test_cli_open_file_with_result() -> None:
    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.open_file.return_value = {"status": "ok", "name": "test.kra", "width": 800, "height": 600}
        mock_get.return_value = mock_client
        result = runner.invoke(app, ["open-file", "/tmp/test.kra"])
        assert result.exit_code == 0
        assert "test.kra" in result.output
