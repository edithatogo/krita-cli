"""Tests for MCP server tool success paths to reach 100% coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import krita_mcp.server as server_module


def test_krita_new_canvas_success() -> None:
    server_module._client = None
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.new_canvas.return_value = {"status": "ok", "width": 800, "height": 600}
        mock_get.return_value = mock_client
        result = server_module.krita_new_canvas(width=800, height=600)
        assert "800x600" in result


def test_krita_set_color_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_color.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_color(color="#ff0000")
        assert "Color set to" in result


def test_krita_set_brush_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_brush.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_brush(preset="Soft", size=50)
        assert "preset=Soft" in result


def test_krita_set_brush_with_opacity() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_brush.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_brush(preset="Soft", size=50, opacity=0.8)
        assert "opacity=0.8" in result


def test_krita_set_brush_no_changes() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_brush.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_brush()
        assert "no changes" in result


def test_krita_stroke_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.stroke.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_stroke(points=[[0, 0], [100, 100]])
        assert "2 points" in result


def test_krita_fill_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.fill.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_fill(x=50, y=50, radius=30)
        assert "Filled at" in result


def test_krita_draw_shape_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.draw_shape.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_draw_shape(shape="rectangle", x=0, y=0)
        assert "Drew rectangle" in result


def test_krita_get_canvas_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_canvas.return_value = {"status": "ok", "path": "/tmp/canvas.png"}
        mock_get.return_value = mock_client
        result = server_module.krita_get_canvas()
        assert "/tmp/canvas.png" in result


def test_krita_get_canvas_error_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_canvas.return_value = {"error": "export failed"}
        mock_get.return_value = mock_client
        result = server_module.krita_get_canvas()
        assert "Error: export failed" in result


def test_krita_undo_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.undo.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_undo()
        assert result == "Undone"


def test_krita_redo_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.redo.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_redo()
        assert result == "Redone"


def test_krita_clear_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.clear.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_clear()
        assert "Canvas cleared" in result


def test_krita_save_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.save.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_save(path="/tmp/test.png")
        assert "Saved to" in result


def test_krita_get_color_at_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_color_at.return_value = {
            "status": "ok",
            "color": "#ff0000",
            "r": 255,
            "g": 0,
            "b": 0,
        }
        mock_get.return_value = mock_client
        result = server_module.krita_get_color_at(x=10, y=20)
        assert "#ff0000" in result


def test_krita_list_brushes_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.list_brushes.return_value = {"brushes": ["Soft", "Hard"]}
        mock_get.return_value = mock_client
        result = server_module.krita_list_brushes()
        assert "Soft" in result


def test_krita_list_brushes_empty() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.list_brushes.return_value = {"brushes": []}
        mock_get.return_value = mock_client
        result = server_module.krita_list_brushes()
        assert "No brushes" in result


def test_krita_open_file_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.open_file.return_value = {"status": "ok", "name": "test.kra", "width": 800, "height": 600}
        mock_get.return_value = mock_client
        result = server_module.krita_open_file(path="/tmp/test.kra")
        assert "test.kra" in result
