"""Integration tests for MCP error paths to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_mcp import server
from krita_client import KritaError, KritaConnectionError


@pytest.fixture
def mock_client():
    with patch("krita_mcp.server._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_krita_health_connection_error(mock_client) -> None:
    mock_client.health.side_effect = KritaConnectionError("failed")
    result = server.krita_health()
    assert "Cannot connect" in result


def test_krita_health_generic_error(mock_client) -> None:
    mock_client.health.side_effect = KritaError("oops", code="GENERIC")
    result = server.krita_health()
    assert "[GENERIC] oops" in result


def test_krita_new_canvas_error_result(mock_client) -> None:
    mock_client.new_canvas.return_value = {"error": "bad width"}
    result = server.krita_new_canvas()
    assert "Error: bad width" in result


def test_krita_set_color_error(mock_client) -> None:
    mock_client.set_color.return_value = {"error": "bad color"}
    result = server.krita_set_color("#xyz")
    assert "Error: bad color" in result


def test_krita_set_brush_error(mock_client) -> None:
    mock_client.set_brush.return_value = {"error": "bad brush"}
    result = server.krita_set_brush(preset="none")
    assert "Error: bad brush" in result


def test_krita_stroke_error(mock_client) -> None:
    mock_client.stroke.return_value = {"error": "out of bounds"}
    result = server.krita_stroke(points=[[0,0], [1,1]])
    assert "Error: out of bounds" in result


def test_krita_fill_error(mock_client) -> None:
    mock_client.fill.return_value = {"error": "too big"}
    result = server.krita_fill(0, 0, radius=9999)
    assert "Error: too big" in result


def test_krita_draw_shape_error(mock_client) -> None:
    mock_client.draw_shape.return_value = {"error": "invalid shape"}
    result = server.krita_draw_shape("triangle", 0, 0)
    assert "Error: invalid shape" in result


def test_krita_get_canvas_error(mock_client) -> None:
    mock_client.get_canvas.return_value = {"error": "save failed"}
    result = server.krita_get_canvas()
    assert "Error: save failed" in result


def test_krita_undo_error(mock_client) -> None:
    mock_client.undo.return_value = {"error": "nothing to undo"}
    result = server.krita_undo()
    assert "Error: nothing to undo" in result


def test_krita_redo_error(mock_client) -> None:
    mock_client.redo.return_value = {"error": "nothing to redo"}
    result = server.krita_redo()
    assert "Error: nothing to redo" in result


def test_krita_clear_error(mock_client) -> None:
    mock_client.clear.return_value = {"error": "failed"}
    result = server.krita_clear()
    assert "Error: failed" in result


def test_krita_save_error(mock_client) -> None:
    mock_client.save.return_value = {"error": "permission denied"}
    result = server.krita_save("protected.png")
    assert "Error: permission denied" in result


def test_krita_get_color_at_error(mock_client) -> None:
    mock_client.get_color_at.return_value = {"error": "off canvas"}
    result = server.krita_get_color_at(-1, -1)
    assert "Error: off canvas" in result


def test_krita_list_brushes_error(mock_client) -> None:
    mock_client.list_brushes.return_value = {"error": "not found"}
    result = server.krita_list_brushes(filter="nonexistent")
    assert "Error: not found" in result


def test_krita_open_file_error(mock_client) -> None:
    mock_client.open_file.return_value = {"error": "not found"}
    result = server.krita_open_file("missing.kra")
    assert "Error: not found" in result


def test_krita_batch_error_path(mock_client) -> None:
    mock_client.batch_execute.side_effect = KritaError("batch failed")
    result = server.krita_batch(commands=[])
    assert "batch failed" in result


def test_krita_rollback_error(mock_client) -> None:
    mock_client.rollback.return_value = {"error": "id not found"}
    result = server.krita_rollback("invalid")
    assert "Error: id not found" in result


def test_krita_get_command_history_error(mock_client) -> None:
    mock_client.get_command_history.side_effect = KritaError("history error")
    result = server.krita_get_command_history()
    assert "history error" in result


def test_krita_get_canvas_info_error(mock_client) -> None:
    mock_client.get_canvas_info.return_value = {"error": "no canvas"}
    result = server.krita_get_canvas_info()
    assert "Error: no canvas" in result


def test_krita_get_current_color_error(mock_client) -> None:
    mock_client.get_current_color.return_value = {"error": "failed"}
    result = server.krita_get_current_color()
    assert "Error: failed" in result


def test_krita_get_current_brush_error(mock_client) -> None:
    mock_client.get_current_brush.return_value = {"error": "failed"}
    result = server.krita_get_current_brush()
    assert "Error: failed" in result


def test_krita_select_rect_error(mock_client) -> None:
    mock_client.select_rect.return_value = {"error": "failed"}
    result = server.krita_select_rect(0, 0, 0, 0)
    assert "Error: failed" in result


def test_krita_select_ellipse_error(mock_client) -> None:
    mock_client.select_ellipse.return_value = {"error": "failed"}
    result = server.krita_select_ellipse(0, 0, 0, 0)
    assert "Error: failed" in result


def test_krita_select_polygon_error(mock_client) -> None:
    mock_client.select_polygon.return_value = {"error": "failed"}
    result = server.krita_select_polygon([])
    assert "Error: failed" in result


def test_krita_selection_info_error(mock_client) -> None:
    mock_client.selection_info.return_value = {"error": "failed"}
    result = server.krita_selection_info()
    assert "Error: failed" in result


def test_krita_clear_selection_error(mock_client) -> None:
    mock_client.clear_selection.return_value = {"error": "failed"}
    result = server.krita_clear_selection()
    assert "Error: failed" in result


def test_krita_invert_selection_error(mock_client) -> None:
    mock_client.invert_selection.return_value = {"error": "failed"}
    result = server.krita_invert_selection()
    assert "Error: failed" in result


def test_krita_fill_selection_error(mock_client) -> None:
    mock_client.fill_selection.return_value = {"error": "failed"}
    result = server.krita_fill_selection()
    assert "Error: failed" in result


def test_krita_deselect_error(mock_client) -> None:
    mock_client.deselect.return_value = {"error": "failed"}
    result = server.krita_deselect()
    assert "Error: failed" in result


def test_krita_select_by_color_error(mock_client) -> None:
    mock_client.select_by_color.return_value = {"error": "failed"}
    result = server.krita_select_by_color()
    assert "Error: failed" in result


def test_krita_select_by_alpha_error(mock_client) -> None:
    mock_client.select_by_alpha.return_value = {"error": "failed"}
    result = server.krita_select_by_alpha()
    assert "Error: failed" in result


def test_krita_transform_selection_error(mock_client) -> None:
    mock_client.transform_selection.return_value = {"error": "failed"}
    result = server.krita_transform_selection()
    assert "Error: failed" in result


def test_krita_grow_selection_error(mock_client) -> None:
    mock_client.grow_selection.return_value = {"error": "failed"}
    result = server.krita_grow_selection(1)
    assert "Error: failed" in result


def test_krita_shrink_selection_error(mock_client) -> None:
    mock_client.shrink_selection.return_value = {"error": "failed"}
    result = server.krita_shrink_selection(1)
    assert "Error: failed" in result


def test_krita_border_selection_error(mock_client) -> None:
    mock_client.border_selection.return_value = {"error": "failed"}
    result = server.krita_border_selection(1)
    assert "Error: failed" in result


def test_krita_save_selection_error(mock_client) -> None:
    mock_client.save_selection.return_value = {"error": "failed"}
    result = server.krita_save_selection("test.png")
    assert "Error: failed" in result


def test_krita_load_selection_error(mock_client) -> None:
    mock_client.load_selection.return_value = {"error": "failed"}
    result = server.krita_load_selection("test.png")
    assert "Error: failed" in result


def test_krita_selection_stats_error(mock_client) -> None:
    mock_client.selection_stats.return_value = {"error": "failed"}
    result = server.krita_selection_stats()
    assert "Error: failed" in result


def test_krita_save_selection_channel_error(mock_client) -> None:
    mock_client.save_selection_channel.return_value = {"error": "failed"}
    result = server.krita_save_selection_channel("ch1")
    assert "Error: failed" in result


def test_krita_load_selection_channel_error(mock_client) -> None:
    mock_client.load_selection_channel.return_value = {"error": "failed"}
    result = server.krita_load_selection_channel("ch1")
    assert "Error: failed" in result


def test_krita_list_selection_channels_error(mock_client) -> None:
    mock_client.list_selection_channels.return_value = {"error": "failed"}
    result = server.krita_list_selection_channels()
    assert "Error: failed" in result


def test_krita_security_status_error(mock_client) -> None:
    mock_client.get_security_status.side_effect = KritaError("failed")
    result = server.krita_security_status()
    assert "failed" in result
