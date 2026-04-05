"""Unit tests for the BatchSnapshotStore."""

import sys
from unittest.mock import MagicMock

# Mock krita and PyQt5 before importing kritamcp submodules
mock_krita = MagicMock()
mock_krita.Krita = MagicMock()
mock_krita.Extension = MagicMock
sys.modules["krita"] = mock_krita

mock_qt = MagicMock()
sys.modules["PyQt5"] = mock_qt
sys.modules["PyQt5.QtCore"] = MagicMock()
sys.modules["PyQt5.QtGui"] = MagicMock()

# Import snapshot_store after mocking
from kritamcp.snapshot_store import BatchSnapshotStore

import os
import tempfile
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def store() -> BatchSnapshotStore:
    # Use a temporary directory for snapshots
    tmp_dir = tempfile.mkdtemp()
    store = BatchSnapshotStore(max_snapshots=3, snapshot_dir=tmp_dir)
    yield store
    shutil.rmtree(tmp_dir)


def test_create_and_get_snapshot(store: BatchSnapshotStore) -> None:
    # Create a dummy file
    snapshot_path = os.path.join(store.snapshot_dir, "test.png")
    Path(snapshot_path).touch()
    
    commands = [{"action": "stroke", "params": {}}]
    batch_id = store.create_snapshot(commands, snapshot_path)
    
    snapshot = store.get_snapshot(batch_id)
    assert snapshot is not None
    assert snapshot.batch_id == batch_id
    assert snapshot.commands == commands
    assert snapshot.canvas_before_path == snapshot_path


def test_snapshot_eviction(store: BatchSnapshotStore) -> None:
    # Max snapshots is 3
    paths = []
    ids = []
    for i in range(4):
        path = os.path.join(store.snapshot_dir, f"test_{i}.png")
        Path(path).touch()
        paths.append(path)
        ids.append(store.create_snapshot([], path))
        
    # The first one (index 0) should be evicted
    assert store.get_snapshot(ids[0]) is None
    assert not os.path.exists(paths[0])
    
    # Others should still be there
    for i in range(1, 4):
        assert store.get_snapshot(ids[i]) is not None
        assert os.path.exists(paths[i])


def test_remove_snapshot(store: BatchSnapshotStore) -> None:
    path = os.path.join(store.snapshot_dir, "remove.png")
    Path(path).touch()
    batch_id = store.create_snapshot([], path)
    
    assert os.path.exists(path)
    removed = store.remove_snapshot(batch_id)
    assert removed is True
    assert store.get_snapshot(batch_id) is None
    assert not os.path.exists(path)


def test_clear_store(store: BatchSnapshotStore) -> None:
    for i in range(3):
        path = os.path.join(store.snapshot_dir, f"clear_{i}.png")
        Path(path).touch()
        store.create_snapshot([], path)
        
    store.clear()
    assert len(store._snapshots) == 0
    assert len(os.listdir(store.snapshot_dir)) == 0
