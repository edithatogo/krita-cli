"""Unit tests for command history record model and history store."""

from __future__ import annotations

import importlib.util
import threading
import time
from pathlib import Path

import pytest

from krita_client.models import CommandHistoryRecord


class TestCommandHistoryRecord:
    """Tests for the command history record model."""

    def test_history_record_valid(self) -> None:
        """Valid history record should create successfully."""
        record = CommandHistoryRecord(
            action="set_color",
            params={"color": "#ff0000"},
            timestamp=1234567890.0,
            status="ok",
            duration_ms=15.5,
        )
        assert record.action == "set_color"
        assert record.params == {"color": "#ff0000"}
        assert record.timestamp == 1234567890.0
        assert record.status == "ok"
        assert record.duration_ms == 15.5

    def test_history_record_error_status(self) -> None:
        """History record should support error status."""
        record = CommandHistoryRecord(
            action="stroke",
            params={"points": [[0, 0], [100, 100]]},
            timestamp=1234567890.0,
            status="error",
            duration_ms=5.0,
            error="No active document",
        )
        assert record.status == "error"
        assert record.error == "No active document"

    def test_history_record_sanitized_params(self) -> None:
        """History record should store params for auditing."""
        record = CommandHistoryRecord(
            action="save",
            params={"path": "/home/user/art.png"},
            timestamp=1234567890.0,
            status="ok",
            duration_ms=120.0,
        )
        assert record.params["path"] == "/home/user/art.png"


class TestCommandHistoryStore:
    """Tests for the in-memory command history store."""

    def _get_store_class(self) -> type:
        """Import the history store from the plugin module."""
        store_path = Path(__file__).parent.parent.parent / "krita-plugin" / "kritamcp" / "history_store.py"
        spec = importlib.util.spec_from_file_location("history_store", store_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module.CommandHistoryStore  # type: ignore[no-any-return]

    def test_store_add_and_query(self) -> None:
        """History store should store and return records."""
        StoreClass = self._get_store_class()
        store = StoreClass(max_size=10)

        record = CommandHistoryRecord(
            action="set_color",
            params={"color": "#ff0000"},
            timestamp=1234567890.0,
            status="ok",
            duration_ms=15.5,
        )
        store.add(record.model_dump())

        history = store.query(limit=10)
        assert len(history) == 1
        assert history[0]["action"] == "set_color"

    def test_store_eviction_on_max_size(self) -> None:
        """History store should evict oldest records when full."""
        StoreClass = self._get_store_class()
        store = StoreClass(max_size=3)

        for i in range(5):
            store.add({
                "action": f"action_{i}",
                "params": {},
                "timestamp": float(i),
                "status": "ok",
                "duration_ms": 1.0,
            })

        history = store.query(limit=10)
        assert len(history) == 3
        # Oldest records should be evicted
        assert history[0]["action"] == "action_2"
        assert history[-1]["action"] == "action_4"

    def test_store_query_limit(self) -> None:
        """History store should respect query limit."""
        StoreClass = self._get_store_class()
        store = StoreClass(max_size=10)

        for i in range(5):
            store.add({
                "action": f"action_{i}",
                "params": {},
                "timestamp": float(i),
                "status": "ok",
                "duration_ms": 1.0,
            })

        history = store.query(limit=2)
        assert len(history) == 2
        # Should return most recent first
        assert history[0]["action"] == "action_3"
        assert history[1]["action"] == "action_4"

    def test_store_thread_safety(self) -> None:
        """History store should be thread-safe under concurrent access."""
        StoreClass = self._get_store_class()
        store = StoreClass(max_size=1000)
        lock = threading.Lock()
        added_count = 0

        def add_records() -> None:
            nonlocal added_count
            for i in range(50):
                store.add({
                    "action": "test",
                    "params": {"i": i},
                    "timestamp": time.monotonic(),
                    "status": "ok",
                    "duration_ms": 1.0,
                })
                with lock:
                    added_count += 1

        threads = [threading.Thread(target=add_records) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert added_count == 500
        # Store should have at most max_size records
        assert len(store.query(limit=1000)) <= 1000
