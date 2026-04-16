"""Integration tests for the 'krita batch' CLI command."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from krita_cli.app import app
from krita_client import KritaClient, KritaError

runner = CliRunner()


def test_cli_batch_success(tmp_path) -> None:
    # Create a dummy batch file
    batch_file = tmp_path / "commands.json"
    commands = [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "undo", "params": {}},
    ]
    batch_file.write_text(json.dumps(commands))

    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.batch_execute.return_value = {
            "status": "ok",
            "results": [
                {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
                {"action": "undo", "status": "ok", "result": {"status": "ok"}},
            ],
            "count": 2,
        }
        mock_get.return_value = mock_client

        result = runner.invoke(app, ["batch", str(batch_file)])

        assert result.exit_code == 0
        assert "Batch: ok" in result.stdout
        assert "2 succeeded, 0 failed out of 2" in result.stdout
        # Note: we check batch_execute because we updated the CLI to use it
        mock_client.batch_execute.assert_called_once_with(commands, stop_on_error=False)


def test_cli_batch_invalid_json(tmp_path) -> None:
    batch_file = tmp_path / "bad.json"
    batch_file.write_text("{not json]")

    result = runner.invoke(app, ["batch", str(batch_file)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_cli_batch_not_list(tmp_path) -> None:
    batch_file = tmp_path / "object.json"
    batch_file.write_text(json.dumps({"action": "set_color"}))

    result = runner.invoke(app, ["batch", str(batch_file)])
    assert result.exit_code == 1
    assert "must contain an array of commands" in result.stdout


def test_cli_batch_stop_on_error(tmp_path) -> None:
    batch_file = tmp_path / "commands.json"
    batch_file.write_text(json.dumps([{"action": "undo"}]))

    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.batch_execute.return_value = {"status": "ok"}
        mock_get.return_value = mock_client

        result = runner.invoke(app, ["batch", str(batch_file), "--stop-on-error"])

        assert result.exit_code == 0
        mock_client.batch_execute.assert_called_once_with([{"action": "undo"}], stop_on_error=True)


def test_cli_batch_partial_error(tmp_path) -> None:
    batch_file = tmp_path / "commands.json"
    batch_file.write_text(json.dumps([{"action": "invalid"}]))

    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.batch_execute.return_value = {
            "status": "partial",
            "results": [
                {"action": "invalid", "status": "error", "error": "Unknown action"},
            ],
            "count": 1,
            "batch_id": "b123",
        }
        mock_get.return_value = mock_client

        result = runner.invoke(app, ["batch", str(batch_file)])

        assert result.exit_code == 0
        assert "Batch: partial" in result.stdout
        assert "Unknown action" in result.stdout
        assert "Batch ID: b123" in result.stdout


def test_cli_batch_full_error(tmp_path) -> None:
    batch_file = tmp_path / "commands.json"
    batch_file.write_text(json.dumps([{"action": "undo"}]))

    with patch("krita_cli._shared._get_client") as mock_get:
        mock_client = MagicMock(spec=KritaClient)
        mock_client.batch_execute.side_effect = KritaError("Total failure")
        mock_get.return_value = mock_client

        result = runner.invoke(app, ["batch", str(batch_file)])
        assert result.exit_code == 1
        assert "Total failure" in result.stdout


def test_cli_batch_missing_file() -> None:
    result = runner.invoke(app, ["batch", "nonexistent.json"])
    assert result.exit_code == 1
    assert "Cannot read" in result.stdout
