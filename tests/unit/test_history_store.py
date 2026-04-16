"""Unit tests for the CommandHistory class."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from krita_cli.history import CommandHistory
from krita_client import KritaError


@pytest.fixture
def history() -> CommandHistory:
    return CommandHistory()


def test_enable_recording(history) -> None:
    history.enable_recording("test.json")
    assert history.is_recording()
    assert history._history_file == Path("test.json")


def test_disable_recording(history) -> None:
    history.enable_recording()
    history.disable_recording()
    assert not history.is_recording()


def test_record_command_in_memory(history) -> None:
    history.record_command("stroke", {"points": [[0, 0]]}, {"status": "ok"})
    h = history.get_history()
    assert len(h) == 1
    assert h[0]["action"] == "stroke"


def test_record_command_persistence(history, tmp_path) -> None:
    file_path = tmp_path / "history.json"
    history.enable_recording(file_path)
    history.record_command("set_color", {"color": "#ff0000"}, {"status": "ok"})

    assert file_path.exists()
    data = json.loads(file_path.read_text())
    assert len(data) == 1
    assert data[0]["action"] == "set_color"


def test_clear_history(history) -> None:
    history.record_command("undo", {}, {"status": "ok"})
    history.clear_history()
    assert len(history.get_history()) == 0


def test_load_history_json(history, tmp_path) -> None:
    file_path = tmp_path / "test_load.json"
    data = [{"action": "stroke", "params": {}}]
    file_path.write_text(json.dumps(data))

    loaded = history.load_history(file_path)
    assert len(loaded) == 1
    assert loaded[0]["action"] == "stroke"


def test_load_history_jsonl(history, tmp_path) -> None:
    file_path = tmp_path / "test_load.jsonl"
    file_path.write_text('{"action": "a"}\n{"action": "b"}\n')

    loaded = history.load_history(file_path)
    assert len(loaded) == 2
    assert loaded[0]["action"] == "a"
    assert loaded[1]["action"] == "b"


def test_rollback_batch_success(history) -> None:
    client = MagicMock()
    client.undo.return_value = {"status": "ok"}

    results = history.rollback_batch(3, client)
    assert len(results) == 3
    assert all(r["status"] == "ok" for r in results)
    assert client.undo.call_count == 3


def test_rollback_batch_failure(history) -> None:
    client = MagicMock()
    client.undo.side_effect = KritaError("Undo failed", code="INTERNAL_ERROR")

    results = history.rollback_batch(1, client)
    assert len(results) == 1
    assert results[0]["status"] == "error"
    assert "Undo failed" in results[0]["error"]


def test_replay_commands_in_memory(history) -> None:
    history.record_command("stroke", {}, {"status": "ok"})
    client = MagicMock()
    client.send_command.return_value = {"status": "ok"}

    results = history.replay_commands(client=client)
    assert len(results) == 1
    assert results[0]["action"] == "stroke"
    client.send_command.assert_called_once_with("stroke", {})


def test_replay_commands_from_file(history, tmp_path) -> None:
    file_path = tmp_path / "replay.json"
    file_path.write_text(json.dumps([{"action": "fill", "params": {"x": 10}}]))

    client = MagicMock()
    client.send_command.return_value = {"status": "ok"}

    results = history.replay_commands(file_path=file_path, client=client)
    assert len(results) == 1
    assert results[0]["action"] == "fill"
    client.send_command.assert_called_once_with("fill", {"x": 10})


def test_replay_commands_error_response(history) -> None:
    history.record_command("stroke", {}, {"status": "ok"})
    client = MagicMock()
    # Ensure the mock returns exactly what we want
    client.send_command.return_value = {"status": "error", "error": "failed"}

    results = history.replay_commands(client=client)
    assert results[0]["action"] == "stroke"
    assert results[0]["status"] == "error"
    assert results[0]["result"]["error"] == "failed"


def test_replay_commands_exception(history) -> None:
    history.record_command("stroke", {}, {"status": "ok"})
    client = MagicMock()
    client.send_command.side_effect = KritaError("timeout")

    results = history.replay_commands(client=client)
    assert results[0]["status"] == "error"


def test_record_command_persistence_error(history, tmp_path) -> None:
    # Trigger error by using a directory as a file path
    file_path = tmp_path / "dir"
    file_path.mkdir()
    history.enable_recording(file_path)

    # Should NOT raise PermissionError anymore
    history.record_command("stroke", {}, {"status": "ok"})
    # Verify it still recorded in memory
    assert len(history.get_history()) == 1


def test_load_history_not_found(history, tmp_path) -> None:
    file_path = tmp_path / "missing.json"
    assert history.load_history(file_path) == []


def test_module_functions() -> None:
    from krita_cli import history as history_mod

    history_mod.enable_recording()
    assert history_mod.is_recording()
    history_mod.disable_recording()
    assert not history_mod.is_recording()

    history_mod.clear_history()
    history_mod.record_command("a", {}, {})
    assert len(history_mod.get_history()) == 1

    client = MagicMock()
    client.send_command.return_value = {"status": "ok"}
    results = history_mod.replay_commands(client=client)
    assert len(results) == 1

    client.undo.return_value = {"status": "ok"}
    results = history_mod.rollback_batch(1, client)
    assert len(results) == 1

    assert history_mod.get_system_log_path().name == "history.log"


def test_systemic_logging_exception() -> None:
    from krita_cli.history import CommandHistory

    with patch("krita_cli.history.json.dumps", side_effect=Exception("JSON error")):
        history = CommandHistory()
        # Should not raise
        history.record_command("test", {}, {"status": "ok"})
