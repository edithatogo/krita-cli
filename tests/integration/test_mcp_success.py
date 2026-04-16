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


def test_krita_select_rect_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_rect.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_rect(x=10, y=20, width=100, height=200)
        assert "rectangle" in result


def test_krita_select_ellipse_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_ellipse.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_ellipse(cx=50, cy=50, rx=30, ry=20)
        assert "ellipse" in result


def test_krita_select_polygon_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_polygon.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_polygon(points=[[0, 0], [100, 0], [50, 100]])
        assert "polygon" in result


def test_krita_selection_info_has_selection() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.selection_info.return_value = {
            "status": "ok", "has_selection": True,
            "bounds": {"x": 10, "y": 20, "width": 100, "height": 200},
        }
        mock_get.return_value = mock_client
        result = server_module.krita_selection_info()
        assert "Selection" in result


def test_krita_selection_info_no_selection() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.selection_info.return_value = {"status": "ok", "has_selection": False}
        mock_get.return_value = mock_client
        result = server_module.krita_selection_info()
        assert "No active" in result


def test_krita_clear_selection_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.clear_selection.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_clear_selection()
        assert "Cleared" in result


def test_krita_invert_selection_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.invert_selection.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_invert_selection()
        assert "Inverted" in result


def test_krita_fill_selection_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.fill_selection.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_fill_selection()
        assert "Filled" in result


def test_krita_deselect_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.deselect.return_value = {"status": "ok"}
        mock_get.return_value = mock_client
        result = server_module.krita_deselect()
        assert "Deselect" in result


def test_krita_list_tools_success() -> None:
    result = server_module.krita_list_tools()
    assert "krita_stroke" in result
    assert "krita_select_rect" in result
    assert "40 total" in result


def test_krita_get_canvas_info_full() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_canvas_info.return_value = {
            "status": "ok",
            "name": "test.kra",
            "width": 1000,
            "height": 1000,
            "color_model": "RGBA",
            "color_depth": "U8",
        }
        mock_get.return_value = mock_client
        result = server_module.krita_get_canvas_info()
        assert "name=test.kra" in result
        assert "width=1000" in result
        assert "height=1000" in result
        assert "color_model=RGBA" in result
        assert "color_depth=U8" in result


def test_krita_get_current_color_full() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_current_color.return_value = {
            "status": "ok",
            "foreground": "#ff0000",
            "background": "#000000",
        }
        mock_get.return_value = mock_client
        result = server_module.krita_get_current_color()
        assert "foreground: #ff0000" in result
        assert "background: #000000" in result


def test_krita_get_current_brush_full() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_current_brush.return_value = {
            "status": "ok",
            "preset": "Soft",
            "size": 50.0,
            "opacity": 1.0,
        }
        mock_get.return_value = mock_client
        result = server_module.krita_get_current_brush()
        assert "preset=Soft" in result
        assert "size=50.0" in result
        assert "opacity=1.0" in result
