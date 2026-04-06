"""Tests for MCP server error-in-result branches (client returns error dict)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import krita_mcp.server as server_module


def test_krita_set_color_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_color.return_value = {"error": "invalid color format"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_color(color="invalid")
        assert "Error: invalid color format" in result


def test_krita_stroke_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.stroke.return_value = {"error": "need at least 2 points"}
        mock_get.return_value = mock_client
        result = server_module.krita_stroke(points=[[0, 0]])
        assert "Error: need at least 2 points" in result


def test_krita_fill_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.fill.return_value = {"error": "out of bounds"}
        mock_get.return_value = mock_client
        result = server_module.krita_fill(x=0, y=0)
        assert "Error: out of bounds" in result


def test_krita_draw_shape_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.draw_shape.return_value = {"error": "unsupported shape"}
        mock_get.return_value = mock_client
        result = server_module.krita_draw_shape(shape="triangle", x=0, y=0)
        assert "Error: unsupported shape" in result


def test_krita_get_canvas_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_canvas.return_value = {"error": "export failed"}
        mock_get.return_value = mock_client
        result = server_module.krita_get_canvas()
        assert "Error: export failed" in result


def test_krita_undo_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.undo.return_value = {"error": "nothing to undo"}
        mock_get.return_value = mock_client
        result = server_module.krita_undo()
        assert "Error: nothing to undo" in result


def test_krita_redo_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.redo.return_value = {"error": "nothing to redo"}
        mock_get.return_value = mock_client
        result = server_module.krita_redo()
        assert "Error: nothing to redo" in result


def test_krita_clear_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.clear.return_value = {"error": "no active layer"}
        mock_get.return_value = mock_client
        result = server_module.krita_clear()
        assert "Error: no active layer" in result


def test_krita_save_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.save.return_value = {"error": "permission denied"}
        mock_get.return_value = mock_client
        result = server_module.krita_save(path="/tmp/test.png")
        assert "Error: permission denied" in result


def test_krita_get_color_at_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.get_color_at.return_value = {"error": "out of bounds"}
        mock_get.return_value = mock_client
        result = server_module.krita_get_color_at(x=0, y=0)
        assert "Error: out of bounds" in result


def test_krita_list_brushes_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.list_brushes.return_value = {"error": "failed to list"}
        mock_get.return_value = mock_client
        result = server_module.krita_list_brushes()
        assert "Error: failed to list" in result


def test_krita_open_file_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.open_file.return_value = {"error": "file not found"}
        mock_get.return_value = mock_client
        result = server_module.krita_open_file(path="/tmp/missing.kra")
        assert "Error: file not found" in result


def test_krita_new_canvas_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.new_canvas.return_value = {"error": "dimensions too large"}
        mock_get.return_value = mock_client
        result = server_module.krita_new_canvas(width=100000, height=100000)
        assert "Error: dimensions too large" in result


def test_krita_set_brush_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.set_brush.return_value = {"error": "preset not found"}
        mock_get.return_value = mock_client
        result = server_module.krita_set_brush(preset="nonexistent")
        assert "Error: preset not found" in result


def test_krita_select_rect_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_rect.return_value = {"error": "invalid dimensions"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_rect(x=0, y=0, width=0, height=0)
        assert "Error: invalid dimensions" in result


def test_krita_select_ellipse_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_ellipse.return_value = {"error": "no active document"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_ellipse(cx=0, cy=0, rx=50, ry=50)
        assert "Error: no active document" in result


def test_krita_select_polygon_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.select_polygon.return_value = {"error": "need at least 3 points"}
        mock_get.return_value = mock_client
        result = server_module.krita_select_polygon(points=[[0, 0]])
        assert "Error: need at least 3 points" in result


def test_krita_selection_info_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.selection_info.return_value = {"error": "no active document"}
        mock_get.return_value = mock_client
        result = server_module.krita_selection_info()
        assert "Error: no active document" in result


def test_krita_clear_selection_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.clear_selection.return_value = {"error": "connection failed"}
        mock_get.return_value = mock_client
        result = server_module.krita_clear_selection()
        assert "Error: connection failed" in result


def test_krita_invert_selection_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.invert_selection.return_value = {"error": "no active document"}
        mock_get.return_value = mock_client
        result = server_module.krita_invert_selection()
        assert "Error: no active document" in result


def test_krita_fill_selection_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.fill_selection.return_value = {"error": "no active view"}
        mock_get.return_value = mock_client
        result = server_module.krita_fill_selection()
        assert "Error: no active view" in result


def test_krita_deselect_error_in_result() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.deselect.return_value = {"error": "connection failed"}
        mock_get.return_value = mock_client
        result = server_module.krita_deselect()
        assert "Error: connection failed" in result
