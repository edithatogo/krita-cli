"""Integration tests for replay CLI commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app
from krita_client import KritaError

runner = CliRunner()


@pytest.fixture
def mock_client():
    with patch("krita_cli._shared._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_replay_dry_run(tmp_path) -> None:
    history_file = tmp_path / "history.json"
    history_file.write_text(json.dumps([{"action": "set_color", "params": {"color": "#ff0000"}}]))

    result = runner.invoke(app, ["replay", str(history_file), "--dry-run"])
    assert result.exit_code == 0
    assert "records are valid" in result.stdout


def test_replay_execution(mock_client, tmp_path) -> None:
    history_file = tmp_path / "history.json"
    history_file.write_text(json.dumps([{"action": "set_color", "params": {"color": "#ff0000"}}]))

    mock_client.send_command.return_value = {"status": "ok"}

    result = runner.invoke(app, ["replay", str(history_file), "--speed", "0"])
    assert result.exit_code == 0
    assert "Replay complete: 1 succeeded" in result.stdout
    mock_client.send_command.assert_called_once_with("set_color", {"color": "#ff0000"})


def test_replay_invalid_json(tmp_path) -> None:
    history_file = tmp_path / "history.json"
    history_file.write_text("invalid json")

    result = runner.invoke(app, ["replay", str(history_file)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_replay_with_errors(mock_client, tmp_path) -> None:
    history_file = tmp_path / "history.json"
    # One valid, one missing action, one with error response, one with exception
    history_file.write_text(
        json.dumps([{"action": "set_color"}, {"params": {}}, {"action": "invalid"}, {"action": "fail"}])
    )

    def mock_send(action, params):
        if action == "set_color":
            return {"status": "ok"}
        if action == "invalid":
            return {"error": {"message": "unknown action"}}
        if action == "fail":
            msg = "timeout"
            raise KritaError(msg)
        return {"status": "ok"}


    mock_client.send_command.side_effect = mock_send

    result = runner.invoke(app, ["replay", str(history_file), "--speed", "0"])
    assert result.exit_code == 0
    assert "1 succeeded, 3 failed" in result.stdout
    assert "missing 'action'" in result.stdout
    assert "unknown action" in result.stdout
    assert "timeout" in result.stdout


def test_replay_with_speed(mock_client, tmp_path) -> None:
    history_file = tmp_path / "history.json"
    history_file.write_text(json.dumps([{"action": "set_color", "duration_ms": 10}]))
    mock_client.send_command.return_value = {"status": "ok"}

    with patch("time.sleep") as mock_sleep:
        result = runner.invoke(app, ["replay", str(history_file), "--speed", "2.0"])
        assert result.exit_code == 0
        mock_sleep.assert_called_once()
