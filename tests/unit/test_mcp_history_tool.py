"""Unit tests for MCP history tool."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from krita_client import KritaError


def _patch_client(result: dict, *, raises: type[Exception] | None = None) -> MagicMock:
    """Create a mocked client that returns *result* or raises *raises* on get_command_history."""
    mock = MagicMock()
    if raises is not None:
        mock.get_command_history.side_effect = raises
    else:
        mock.get_command_history.return_value = result
    return mock


def test_krita_get_command_history_returns_formatted_string() -> None:
    """MCP tool returns a human-readable formatted string with history entries."""
    from krita_mcp.server import krita_get_command_history

    history_data = [
        {"action": "set_color", "status": "ok", "duration_ms": 12.5, "error": None},
        {"action": "stroke", "status": "ok", "duration_ms": 45.0, "error": None},
        {"action": "undo", "status": "error", "duration_ms": 5.0, "error": "NO_ACTIVE_DOCUMENT"},
    ]

    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.return_value = _patch_client({"status": "ok", "history": history_data, "count": 3})
        output = krita_get_command_history(limit=10)

    assert "3 entries" in output
    assert "set_color" in output
    assert "stroke" in output
    assert "NO_ACTIVE_DOCUMENT" in output


def test_krita_get_command_history_empty() -> None:
    """MCP tool returns a friendly message when history is empty."""
    from krita_mcp.server import krita_get_command_history

    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.return_value = _patch_client({"status": "ok", "history": [], "count": 0})
        output = krita_get_command_history()

    assert "No command history" in output


def test_krita_get_command_history_error() -> None:
    """MCP tool formats the error when get_command_history fails."""
    from krita_mcp.server import krita_get_command_history

    error = KritaError("History service unavailable", code="INTERNAL_ERROR")

    with patch("krita_mcp.server._get_client") as mock_get:
        mock_get.return_value = _patch_client({}, raises=error)
        output = krita_get_command_history()

    assert "INTERNAL_ERROR" in output
