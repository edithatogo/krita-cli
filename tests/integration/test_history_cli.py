"""Integration tests for history CLI commands."""

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


def test_history_list(mock_client) -> None:
    mock_client.get_command_history.return_value = {
        "status": "ok",
        "history": [{"action": "set_color", "status": "ok", "duration_ms": 10.5, "error": None}],
        "count": 1,
    }
    result = runner.invoke(app, ["history", "--limit", "10"])
    assert result.exit_code == 0
    assert "set_color" in result.stdout
    assert "10.5" in result.stdout


def test_history_json(mock_client) -> None:
    mock_client.get_command_history.return_value = {
        "status": "ok",
        "history": [],
        "count": 0,
    }
    result = runner.invoke(app, ["history", "--json"])
    assert result.exit_code == 0
    assert '"history": []' in result.stdout


def test_history_empty(mock_client) -> None:
    mock_client.get_command_history.return_value = {
        "status": "ok",
        "history": [],
        "count": 0,
    }
    result = runner.invoke(app, ["history"])
    assert result.exit_code == 0
    assert "No command history recorded" in result.stdout
