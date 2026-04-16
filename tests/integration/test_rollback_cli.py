"""Integration tests for rollback CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app

runner = CliRunner()


@pytest.fixture
def mock_client():
    with patch("krita_cli._shared._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_rollback_success(mock_client) -> None:
    mock_client.rollback.return_value = {"status": "ok", "message": "Success"}
    result = runner.invoke(app, ["rollback", "batch-123"])
    assert result.exit_code == 0
    assert "Rollback successful" in result.stdout
    mock_client.rollback.assert_called_once_with(batch_id="batch-123")


def test_rollback_failure(mock_client) -> None:
    mock_client.rollback.return_value = {"status": "error", "message": "Failed"}
    result = runner.invoke(app, ["rollback", "batch-123"])
    assert result.exit_code == 0
    assert "Rollback failed" in result.stdout
