"""Integration tests for remaining MCP tools to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_mcp import server


@pytest.fixture
def mock_client():
    with patch("krita_mcp.server._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_krita_undo(mock_client) -> None:
    mock_client.undo.return_value = {"status": "ok"}
    result = server.krita_undo()
    assert result == "Undone"


def test_krita_redo(mock_client) -> None:
    mock_client.redo.return_value = {"status": "ok"}
    result = server.krita_redo()
    assert result == "Redone"


def test_krita_clear(mock_client) -> None:
    mock_client.clear.return_value = {"status": "ok"}
    result = server.krita_clear(color="#000000")
    assert "cleared to #000000" in result


def test_krita_save(mock_client) -> None:
    mock_client.save.return_value = {"status": "ok"}
    result = server.krita_save(path="test.png")
    assert "Saved to test.png" in result


def test_krita_get_color_at(mock_client) -> None:
    mock_client.get_color_at.return_value = {"status": "ok", "color": "#ff0000", "r": 255, "g": 0, "b": 0}
    result = server.krita_get_color_at(x=10, y=10)
    assert "#ff0000" in result


def test_krita_list_brushes(mock_client) -> None:
    mock_client.list_brushes.return_value = {"status": "ok", "brushes": ["Soft", "Hard"]}
    result = server.krita_list_brushes()
    assert "Available brushes (2)" in result


def test_krita_open_file(mock_client) -> None:
    mock_client.open_file.return_value = {"status": "ok", "name": "test.kra", "width": 800, "height": 600}
    result = server.krita_open_file(path="test.kra")
    assert "Opened: test.kra" in result


def test_krita_batch_success(mock_client) -> None:
    mock_client.batch_execute.return_value = {"status": "ok", "results": [{"status": "ok"}]}
    result = server.krita_batch(commands=[{"action": "undo"}])
    assert "1 succeeded" in result


def test_krita_batch_with_error(mock_client) -> None:
    mock_client.batch_execute.return_value = {
        "status": "partial",
        "results": [{"action": "undo", "status": "error", "error": "failed"}],
        "batch_id": "b123",
    }
    result = server.krita_batch(commands=[{"action": "undo"}])
    assert "1 failed" in result
    assert "Errors:" in result
    assert "Batch ID: b123" in result


def test_krita_batch_nested_error(mock_client) -> None:
    mock_client.batch_execute.return_value = {
        "status": "partial",
        "results": [{"action": "undo", "status": "error", "result": {"error": {"message": "nested failure"}}}],
    }
    result = server.krita_batch(commands=[{"action": "undo"}])
    assert "nested failure" in result


def test_krita_batch_nested_error_string(mock_client) -> None:
    mock_client.batch_execute.return_value = {
        "status": "partial",
        "results": [{"action": "undo", "status": "error", "result": {"error": "string error"}}],
    }
    result = server.krita_batch(commands=[{"action": "undo"}])
    assert "string error" in result


def test_krita_rollback(mock_client) -> None:
    mock_client.rollback.return_value = {"status": "ok", "message": "rolled back"}
    result = server.krita_rollback(batch_id="b123")
    assert "Rollback complete" in result


def test_krita_get_command_history(mock_client) -> None:
    mock_client.get_command_history.return_value = {
        "status": "ok",
        "history": [{"action": "undo", "status": "ok", "duration_ms": 5.0}],
    }
    result = server.krita_get_command_history()
    assert "Command History (1 entries)" in result


def test_krita_get_canvas_info(mock_client) -> None:
    mock_client.get_canvas_info.return_value = {"status": "ok", "width": 800, "name": "test"}
    result = server.krita_get_canvas_info()
    assert "width=800" in result


def test_krita_get_current_color(mock_client) -> None:
    mock_client.get_current_color.return_value = {"status": "ok", "foreground": "#ff0000", "background": "#000000"}
    result = server.krita_get_current_color()
    assert "foreground: #ff0000" in result


def test_krita_get_current_brush(mock_client) -> None:
    mock_client.get_current_brush.return_value = {"status": "ok", "preset": "Soft"}
    result = server.krita_get_current_brush()
    assert "preset=Soft" in result


def test_krita_get_capabilities(mock_client) -> None:
    mock_client.get_capabilities.return_value = {"status": "ok", "selection_tools": ["rect"]}
    result = server.krita_get_capabilities()
    assert "Available selection tools: rect" in result


def test_krita_security_status(mock_client) -> None:
    mock_client.get_security_status.return_value = {
        "status": "ok",
        "rate_limit": {"current_usage": 0, "max_commands_per_minute": 60},
        "payload_limit": 1024 * 1024,
        "batch_size_limit": 100,
        "max_canvas_dim": 8192,
    }
    result = server.krita_security_status()
    assert "Security status" in result


def test_krita_list_tools(mock_client) -> None:
    result = server.krita_list_tools()
    assert "Available Krita MCP tools" in result
    assert "54 total" in result
