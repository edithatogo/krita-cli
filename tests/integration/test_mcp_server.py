"""Integration tests for krita_mcp server."""

from __future__ import annotations

from unittest.mock import patch

from krita_mcp.server import (
    krita_batch,
    krita_clear,
    krita_draw_shape,
    krita_fill,
    krita_get_canvas,
    krita_get_color_at,
    krita_health,
    krita_list_brushes,
    krita_new_canvas,
    krita_open_file,
    krita_redo,
    krita_save,
    krita_set_color,
    krita_stroke,
    krita_undo,
)


def test_krita_health_connection_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        from krita_client import KritaConnectionError

        mock_get.side_effect = KritaConnectionError("refused")
        result = krita_health()
        assert "Cannot connect to Krita" in result


def test_krita_health_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.health.return_value = {"status": "ok", "plugin": "kritamcp"}
        result = krita_health()
        assert "Krita is running" in result


def test_krita_new_canvas_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.new_canvas.return_value = {"error": "failed"}
        result = krita_new_canvas()
        assert "Error: failed" in result


def test_krita_set_color_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        from krita_client import KritaValidationError

        mock_client = mock_get.return_value
        mock_client.set_color.side_effect = KritaValidationError("bad color")
        result = krita_set_color(color="invalid")
        assert "bad color" in result


def test_krita_stroke_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.stroke.return_value = {"status": "ok"}
        result = krita_stroke(points=[[0, 0], [100, 100]])
        assert "Stroke painted" in result


def test_krita_undo_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.undo.return_value = {"status": "ok"}
        result = krita_undo()
        assert result == "Undone"


def test_krita_redo_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.redo.return_value = {"status": "ok"}
        result = krita_redo()
        assert result == "Redone"


def test_krita_fill_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.fill.return_value = {"status": "ok"}
        result = krita_fill(x=50, y=50)
        assert "Filled at" in result


def test_krita_draw_shape_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.draw_shape.return_value = {"status": "ok"}
        result = krita_draw_shape(shape="rectangle", x=0, y=0)
        assert "Drew rectangle" in result


def test_krita_get_canvas_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.get_canvas.return_value = {"status": "ok", "path": "/tmp/canvas.png"}
        result = krita_get_canvas()
        assert "/tmp/canvas.png" in result


def test_krita_save_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.save.return_value = {"status": "ok"}
        result = krita_save(path="/tmp/test.png")
        assert "Saved to" in result


def test_krita_clear_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.clear.return_value = {"status": "ok"}
        result = krita_clear()
        assert "Canvas cleared" in result


def test_krita_get_color_at_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.get_color_at.return_value = {
            "status": "ok",
            "color": "#ff0000",
            "r": 255,
            "g": 0,
            "b": 0,
        }
        result = krita_get_color_at(x=10, y=20)
        assert "#ff0000" in result


def test_krita_list_brushes_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.list_brushes.return_value = {"brushes": ["Soft", "Hard"]}
        result = krita_list_brushes()
        assert "Soft" in result
        assert "Hard" in result


def test_krita_list_brushes_empty() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.list_brushes.return_value = {"brushes": []}
        result = krita_list_brushes()
        assert "No brushes" in result


def test_krita_open_file_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.open_file.return_value = {
            "status": "ok",
            "name": "test.kra",
            "width": 800,
            "height": 600,
        }
        result = krita_open_file(path="/tmp/test.kra")
        assert "test.kra" in result


def test_krita_batch_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.batch_execute.return_value = {
            "status": "ok",
            "results": [
                {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
                {"action": "stroke", "status": "ok", "result": {"status": "ok"}},
            ],
            "count": 2,
        }
        result = krita_batch(commands=[{"action": "set_color", "params": {"color": "#ff0000"}}])
        assert "2 succeeded" in result


def test_krita_batch_with_errors() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.batch_execute.return_value = {
            "status": "error",
            "results": [
                {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
                {"action": "stroke", "status": "error", "result": {"error": "No active layer"}},
            ],
            "count": 2,
        }
        result = krita_batch(commands=[{"action": "set_color"}, {"action": "stroke"}])
        assert "1 failed" in result
        assert "No active layer" in result


def test_krita_batch_stop_on_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = mock_get.return_value
        mock_client.batch_execute.return_value = {
            "status": "error",
            "results": [
                {"action": "set_color", "status": "error", "error": "No active view"},
            ],
            "count": 1,
        }
        result = krita_batch(commands=[{"action": "set_color"}], stop_on_error=True)
        assert "No active view" in result
