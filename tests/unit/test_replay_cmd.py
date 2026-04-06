"""Unit tests for the replay CLI command."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from krita_cli.app import app

runner = CliRunner()


def test_replay_dry_run_valid(tmp_path) -> None:
    """Dry run should validate all records without executing."""
    records = [
        {"action": "set_color", "params": {"color": "#ff0000"}, "duration_ms": 10.0},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}, "duration_ms": 50.0},
    ]
    replay_file = tmp_path / "replay.json"
    replay_file.write_text(json.dumps(records))

    result = runner.invoke(app, ["replay", "replay", str(replay_file), "--dry-run"])
    assert result.exit_code == 0
    assert "All 2 records are valid" in result.stdout


def test_replay_dry_run_missing_action(tmp_path) -> None:
    """Dry run should fail if a record is missing 'action'."""
    records = [{"params": {"color": "#ff0000"}}]
    replay_file = tmp_path / "replay.json"
    replay_file.write_text(json.dumps(records))

    result = runner.invoke(app, ["replay", "replay", str(replay_file), "--dry-run"])
    assert "Missing 'action'" in result.stdout


def test_replay_invalid_json(tmp_path) -> None:
    """Replay should fail on invalid JSON."""
    replay_file = tmp_path / "bad.json"
    replay_file.write_text("{not json]")

    result = runner.invoke(app, ["replay", "replay", str(replay_file)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_replay_not_a_list(tmp_path) -> None:
    """Replay should fail if JSON is not a list."""
    replay_file = tmp_path / "obj.json"
    replay_file.write_text(json.dumps({"action": "set_color"}))

    result = runner.invoke(app, ["replay", "replay", str(replay_file)])
    assert result.exit_code == 1
    assert "must contain an array" in result.stdout


def test_replay_execution(tmp_path) -> None:
    """Replay should execute commands via the client."""
    records = [
        {"action": "set_color", "params": {"color": "#ff0000"}, "duration_ms": 10.0},
        {"action": "undo", "params": {}, "duration_ms": 5.0},
    ]
    replay_file = tmp_path / "replay.json"
    replay_file.write_text(json.dumps(records))

    with patch("krita_cli._shared._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.send_command.return_value = {"status": "ok"}
        mock_get_client.return_value = mock_client

        result = runner.invoke(app, ["replay", "replay", str(replay_file), "--speed", "0.0"])

        assert result.exit_code == 0
        assert mock_client.send_command.call_count == 2
        assert "2 succeeded" in result.stdout
