import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from krita_client import ClientConfig, KritaClient, KritaError

SYSTEM_HISTORY_DIR = Path.home() / ".krita-cli"
SYSTEM_HISTORY_FILE = SYSTEM_HISTORY_DIR / "history.log"


class CommandHistory:
    """Manages command history recording and replay."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._recording_enabled: bool = False
        self._history_file: Path | None = None

    def enable_recording(self, file_path: str | Path | None = None) -> None:
        """Enable command recording, optionally persisting to a file."""
        self._recording_enabled = True
        self._history_file = Path(file_path) if file_path else None

    def disable_recording(self) -> None:
        """Disable command recording."""
        self._recording_enabled = False

    def is_recording(self) -> bool:
        """Return whether recording is currently enabled."""
        return self._recording_enabled

    def _append_to_system_log(self, entry: dict[str, Any]) -> None:
        """Append a command entry to the systemic history log (JSONL)."""
        try:
            SYSTEM_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
            log_entry = {
                "timestamp": datetime.now(UTC).isoformat(),
                **entry,
            }
            with SYSTEM_HISTORY_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            # Persistent logging should not crash the CLI if it fails (e.g. permission issues)
            pass

    def record_command(
        self,
        action: str,
        params: dict[str, Any] | None,
        result: dict[str, Any] | None,
    ) -> None:
        """Record a command invocation to the in-memory history."""
        entry: dict[str, Any] = {
            "action": action,
            "params": params or {},
            "result": result,
        }
        self._history.append(entry)
        self._append_to_system_log(entry)

        if self._recording_enabled and self._history_file is not None:
            try:
                self._history_file.parent.mkdir(parents=True, exist_ok=True)
                self._history_file.write_text(json.dumps(self._history, indent=2))
            except Exception:
                # Persistent history write should not crash the CLI
                pass

    def get_history(self) -> list[dict[str, Any]]:
        """Return the current command history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the in-memory history."""
        self._history.clear()

    def load_history(self, file_path: str | Path) -> list[dict[str, Any]]:
        """Load command history from a JSON file or JSONL log."""
        path = Path(file_path)
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        # Try parsing as JSONL first (system log)
        if content.startswith("{") and "\n" in content:
            return [json.loads(line) for line in content.splitlines() if line.strip()]

        # Fallback to standard JSON array
        data = json.loads(content)
        if not isinstance(data, list):
            return []
        return data

    def rollback_batch(self, count: int, client: KritaClient) -> list[dict[str, Any]]:
        """Rollback the last N operations by calling undo."""
        results: list[dict[str, Any]] = []
        for i in range(count):
            try:
                result = client.undo()
                results.append({"action": "undo", "status": "ok", "iteration": i + 1, "result": result})
            except KritaError as exc:
                results.append({"action": "undo", "status": "error", "iteration": i + 1, "error": exc.message})
        return results

    def replay_commands(
        self,
        file_path: str | Path | None = None,
        client: KritaClient | None = None,
    ) -> list[dict[str, Any]]:
        """Replay recorded commands against a Krita client.

        If *file_path* is given, load history from that file.
        Otherwise replay the in-memory history.

        Returns a list of results (one per command).
        """
        commands = self.load_history(file_path) if file_path is not None else self.get_history()

        if client is None:
            client = KritaClient(ClientConfig())

        results: list[dict[str, Any]] = []
        for entry in commands:
            action = entry["action"]
            params = entry.get("params", {})
            try:
                result = client.send_command(action, params)
                status = result.get("status", "ok")
                results.append({"action": action, "status": status, "result": result})
            except KritaError as exc:
                results.append({"action": action, "status": "error", "error": exc.message})

        return results


# Module-level singleton for backward compatibility
_history = CommandHistory()


def enable_recording(file_path: str | Path | None = None) -> None:
    """Enable command recording, optionally persisting to a file."""
    _history.enable_recording(file_path)


def disable_recording() -> None:
    """Disable command recording."""
    _history.disable_recording()


def is_recording() -> bool:
    """Return whether recording is currently enabled."""
    return _history.is_recording()


def record_command(
    action: str,
    params: dict[str, Any] | None,
    result: dict[str, Any] | None,
) -> None:
    """Record a command invocation to the in-memory history."""
    _history.record_command(action, params, result)


def get_history() -> list[dict[str, Any]]:
    """Return the current command history."""
    return _history.get_history()


def clear_history() -> None:
    """Clear the in-memory history."""
    _history.clear_history()


def load_history(file_path: str | Path) -> list[dict[str, Any]]:
    """Load command history from a JSON file."""
    return _history.load_history(file_path)


def replay_commands(
    file_path: str | Path | None = None,
    client: KritaClient | None = None,
) -> list[dict[str, Any]]:
    """Replay recorded commands against a Krita client."""
    return _history.replay_commands(file_path=file_path, client=client)


def rollback_batch(count: int, client: KritaClient) -> list[dict[str, Any]]:
    """Rollback the last N operations by calling undo."""
    return _history.rollback_batch(count, client)


def get_system_log_path() -> Path:
    """Return the path to the systemic history log."""
    return SYSTEM_HISTORY_FILE
