"""Additional integration tests for MCP server error paths."""

from __future__ import annotations

from unittest.mock import patch

from krita_client import KritaError
from krita_mcp.server import (
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
    krita_set_brush,
    krita_undo,
)


def _mock_error(msg: str, code: str | None = None) -> KritaError:
    return KritaError(msg, code=code)


def test_krita_new_canvas_generic_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("generic error")
        result = krita_new_canvas()
        assert "generic error" in result


def test_krita_set_brush_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("brush error")
        result = krita_set_brush(preset="test")
        assert "brush error" in result


def test_krita_fill_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("fill error")
        result = krita_fill(x=0, y=0)
        assert "fill error" in result


def test_krita_draw_shape_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("shape error")
        result = krita_draw_shape(shape="circle", x=0, y=0)
        assert "shape error" in result


def test_krita_get_canvas_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("export error")
        result = krita_get_canvas()
        assert "export error" in result


def test_krita_undo_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("undo error")
        result = krita_undo()
        assert "undo error" in result


def test_krita_redo_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("redo error")
        result = krita_redo()
        assert "redo error" in result


def test_krita_clear_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("clear error")
        result = krita_clear()
        assert "clear error" in result


def test_krita_save_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("save error")
        result = krita_save(path="/tmp/test.png")
        assert "save error" in result


def test_krita_get_color_at_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("color error")
        result = krita_get_color_at(x=0, y=0)
        assert "color error" in result


def test_krita_list_brushes_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("brush error")
        result = krita_list_brushes()
        assert "brush error" in result


def test_krita_open_file_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("open error")
        result = krita_open_file(path="/tmp/test.kra")
        assert "open error" in result


def test_krita_health_with_code() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = _mock_error("connection refused", code="CONN_REFUSED")
        result = krita_health()
        assert "CONN_REFUSED" in result
