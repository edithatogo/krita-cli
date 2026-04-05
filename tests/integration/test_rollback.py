"""Integration tests for rollback functionality (using mocks)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app
from krita_client.models import ErrorCode
from krita_mcp.server import krita_rollback

runner = CliRunner()


def test_cli_rollback_success() -> None:
    """Test CLI rollback command with successful response."""
    mock_response = {"status": "ok", "message": "Rolled back batch-123"}

    with patch("krita_cli._shared._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.rollback.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["rollback", "batch-123"])

        assert result.exit_code == 0
        assert "ok" in result.stdout
        assert "Rolled back batch-123" in result.stdout
        mock_client.rollback.assert_called_once_with(batch_id="batch-123")


def test_mcp_rollback_success() -> None:
    """Test MCP krita_rollback tool with successful response."""
    mock_response = {"status": "ok", "message": "Restored to new layer"}

    with patch("krita_mcp.server._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.rollback.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = krita_rollback(batch_id="batch-123")

        assert "Rollback complete" in result
        assert "Restored to new layer" in result
        mock_client.rollback.assert_called_once_with(batch_id="batch-123")


def test_mcp_rollback_not_found() -> None:
    """Test MCP krita_rollback tool when batch is not found."""
    # The MCP server code:
    # except KritaError as exc:
    #     return _format_error(exc)
    
    from krita_client import KritaCommandError
    
    with patch("krita_mcp.server._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.rollback.side_effect = KritaCommandError(
            message="Batch not found",
            code="BATCH_NOT_FOUND",
            recoverable=True
        )
        mock_get_client.return_value = mock_client

        result = krita_rollback(batch_id="invalid-id")

        assert "[BATCH_NOT_FOUND]" in result
        assert "Batch not found" in result
