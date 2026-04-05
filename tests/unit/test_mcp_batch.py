"""Unit tests for MCP server batch tool."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_mcp.server import krita_batch


def test_krita_batch_tool_success() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.batch_execute.return_value = {
            "status": "ok",
            "results": [
                {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
            ],
            "count": 1,
        }
        mock_get.return_value = mock_client
        
        result = krita_batch(commands=[{"action": "set_color"}])
        assert "Batch: 1 succeeded, 0 failed out of 1" in result


def test_krita_batch_tool_with_errors() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.batch_execute.return_value = {
            "status": "error",
            "results": [
                {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
                {"action": "stroke", "status": "error", "error": "No active layer"},
            ],
            "count": 2,
        }
        mock_get.return_value = mock_client
        
        result = krita_batch(commands=[{"action": "set_color"}, {"action": "stroke"}])
        assert "1 succeeded, 1 failed out of 2" in result
        assert "stroke: No active layer" in result


def test_krita_batch_tool_with_nested_error() -> None:
    with patch("krita_mcp.server._get_client") as mock_get:
        mock_client = MagicMock()
        mock_client.batch_execute.return_value = {
            "status": "error",
            "results": [
                {"action": "stroke", "status": "error", "result": {"error": "Out of bounds"}},
            ],
            "count": 1,
        }
        mock_get.return_value = mock_client
        
        result = krita_batch(commands=[{"action": "stroke"}])
        assert "stroke: Out of bounds" in result
