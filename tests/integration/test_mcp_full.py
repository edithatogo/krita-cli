"""Tests for MCP server _get_client singleton and _format_error."""

from __future__ import annotations

from unittest.mock import patch

import krita_mcp.server as server_module
from krita_client import ClientConfig, KritaClient, KritaError


def test_get_client_creates_new() -> None:
    """Test that _get_client creates a new client when none exists."""
    server_module._client = None
    with patch("krita_mcp.server.ClientConfig") as mock_config:
        mock_config.return_value = ClientConfig()
        with patch("krita_mcp.server.KritaClient") as mock_kc:
            mock_kc.return_value = KritaClient()
            client = server_module._get_client()
            assert client is not None
            mock_kc.assert_called_once()


def test_get_client_returns_existing() -> None:
    """Test that _get_client returns existing client."""
    existing = KritaClient()
    server_module._client = existing
    client = server_module._get_client()
    assert client is existing
    server_module._client = None


def test_format_error_with_code() -> None:
    """Test _format_error includes code."""
    err = KritaError("something failed", code="ERR_001")
    result = server_module._format_error(err)
    assert "[ERR_001]" in result
    assert "something failed" in result


def test_format_error_without_code() -> None:
    """Test _format_error without code."""
    err = KritaError("something failed")
    result = server_module._format_error(err)
    assert result == "something failed"


def test_krita_stroke_error() -> None:
    """Test stroke tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("stroke failed")
        result = server_module.krita_stroke(points=[[0, 0], [100, 100]])
        assert "stroke failed" in result


def test_krita_set_brush_error_with_details() -> None:
    """Test set-brush tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("brush not found")
        result = server_module.krita_set_brush(preset="nonexistent")
        assert "brush not found" in result


def test_krita_draw_shape_error() -> None:
    """Test draw-shape tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("shape failed")
        result = server_module.krita_draw_shape(shape="rectangle", x=0, y=0)
        assert "shape failed" in result


def test_krita_get_canvas_error() -> None:
    """Test get-canvas tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("export failed")
        result = server_module.krita_get_canvas()
        assert "export failed" in result


def test_krita_save_error() -> None:
    """Test save tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("save failed")
        result = server_module.krita_save(path="/tmp/test.png")
        assert "save failed" in result


def test_krita_clear_error() -> None:
    """Test clear tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("clear failed")
        result = server_module.krita_clear()
        assert "clear failed" in result


def test_krita_get_color_at_error() -> None:
    """Test get-color-at tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("color read failed")
        result = server_module.krita_get_color_at(x=0, y=0)
        assert "color read failed" in result


def test_krita_list_brushes_error() -> None:
    """Test list-brushes tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("brush list failed")
        result = server_module.krita_list_brushes()
        assert "brush list failed" in result


def test_krita_open_file_error() -> None:
    """Test open-file tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("open failed")
        result = server_module.krita_open_file(path="/tmp/test.kra")
        assert "open failed" in result


def test_krita_new_canvas_error() -> None:
    """Test new-canvas tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("canvas creation failed")
        result = server_module.krita_new_canvas()
        assert "canvas creation failed" in result


def test_krita_set_color_error() -> None:
    """Test set-color tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("color set failed")
        result = server_module.krita_set_color(color="#ff0000")
        assert "color set failed" in result


def test_krita_fill_error() -> None:
    """Test fill tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("fill failed")
        result = server_module.krita_fill(x=0, y=0)
        assert "fill failed" in result


def test_krita_undo_error() -> None:
    """Test undo tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("undo failed")
        result = server_module.krita_undo()
        assert "undo failed" in result


def test_krita_redo_error() -> None:
    """Test redo tool error path."""
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.side_effect = KritaError("redo failed")
        result = server_module.krita_redo()
        assert "redo failed" in result
