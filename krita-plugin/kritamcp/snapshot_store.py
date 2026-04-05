"""Thread-safe in-memory store for batch execution snapshots.

Each snapshot contains the batch ID, commands executed, and the path to a
temporary PNG export of the canvas *before* the batch was run.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class BatchSnapshot:
    """Snapshot of a batch execution for potential rollback."""

    batch_id: str
    commands: list[dict[str, Any]]
    canvas_before_path: str
    timestamp: float


class BatchSnapshotStore:
    """Thread-safe store for batch execution snapshots with file cleanup.

    Stores a configurable maximum number of snapshots. When the limit is reached,
    the oldest snapshot is evicted and its associated temporary file is deleted.
    """

    def __init__(self, max_snapshots: int = 50, snapshot_dir: str | None = None) -> None:
        self._max_snapshots = max_snapshots
        self._snapshots: dict[str, BatchSnapshot] = {}
        self._order: deque[str] = deque()
        self._lock = threading.Lock()

        if snapshot_dir is None:
            # Default to a subdirectory in the user's temp or home directory
            import tempfile
            self._snapshot_dir = os.path.join(tempfile.gettempdir(), "kritamcp", "snapshots")
        else:
            self._snapshot_dir = snapshot_dir

        if not os.path.exists(self._snapshot_dir):
            os.makedirs(self._snapshot_dir, exist_ok=True)

    def create_snapshot(self, commands: list[dict[str, Any]], canvas_before_path: str) -> str:
        """Create a new snapshot and return the generated batch ID."""
        batch_id = str(uuid.uuid4())
        snapshot = BatchSnapshot(
            batch_id=batch_id,
            commands=commands,
            canvas_before_path=canvas_before_path,
            timestamp=time.time(),
        )

        with self._lock:
            # Evict oldest if limit reached
            if len(self._order) >= self._max_snapshots:
                self._evict_oldest()

            self._snapshots[batch_id] = snapshot
            self._order.append(batch_id)

        return batch_id

    def get_snapshot(self, batch_id: str) -> BatchSnapshot | None:
        """Retrieve a snapshot by its batch ID."""
        with self._lock:
            return self._snapshots.get(batch_id)

    def remove_snapshot(self, batch_id: str) -> bool:
        """Remove a snapshot and delete its associated temporary file."""
        with self._lock:
            if batch_id in self._snapshots:
                snapshot = self._snapshots.pop(batch_id)
                self._order.remove(batch_id)
                self._delete_file(snapshot.canvas_before_path)
                return True
        return False

    def _evict_oldest(self) -> None:
        """Evict the oldest snapshot (must be called under lock)."""
        if self._order:
            oldest_id = self._order.popleft()
            snapshot = self._snapshots.pop(oldest_id)
            self._delete_file(snapshot.canvas_before_path)

    def _delete_file(self, path: str) -> None:
        """Safely delete a file if it exists."""
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                # Log or ignore if deletion fails (temp files should be cleaned by OS eventually anyway)
                pass

    @property
    def snapshot_dir(self) -> str:
        """Directory where snapshot temporary files are stored."""
        return self._snapshot_dir

    def clear(self) -> None:
        """Clear all snapshots and delete all associated files."""
        with self._lock:
            for snapshot in self._snapshots.values():
                self._delete_file(snapshot.canvas_before_path)
            self._snapshots.clear()
            self._order.clear()
