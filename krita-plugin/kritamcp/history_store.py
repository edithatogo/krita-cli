"""Thread-safe in-memory command history store with LRU eviction.

This module is kept separate from the main plugin file so it can be
imported and tested independently without the Krita runtime.
"""

from __future__ import annotations

import threading
from collections import deque
from typing import Any


class CommandHistoryStore:
    """Thread-safe in-memory store for command execution history.

    Stores command records with a configurable maximum size.
    When the store is full, the oldest records are evicted (FIFO/LRU).
    """

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._records: deque[dict[str, Any]] = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def add(self, record: dict[str, Any]) -> None:
        """Add a command record to the history store.

        If the store is full, the oldest record is automatically evicted.
        """
        with self._lock:
            self._records.append(record)

    def query(self, limit: int = 20) -> list[dict[str, Any]]:
        """Query the history store, returning the most recent records.

        Args:
            limit: Maximum number of records to return. Defaults to 20.

        Returns:
            List of command records, most recent first.
        """
        with self._lock:
            # Return most recent first (deque is ordered oldest-first)
            records = list(self._records)
            return records[-limit:] if limit < len(records) else records

    @property
    def max_size(self) -> int:
        """Maximum number of records the store can hold."""
        return self._max_size

    @max_size.setter
    def max_size(self, value: int) -> None:
        """Update the maximum size (does not resize existing data)."""
        self._max_size = value

    @property
    def size(self) -> int:
        """Current number of records in the store."""
        with self._lock:
            return len(self._records)

    def clear(self) -> None:
        """Clear all records from the store."""
        with self._lock:
            self._records.clear()
