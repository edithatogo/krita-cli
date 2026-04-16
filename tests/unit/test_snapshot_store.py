"""Unit tests for the BatchSnapshotStore."""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Mock krita and PyQt5 before importing kritamcp submodules
mock_krita = MagicMock()
mock_krita.Krita = MagicMock()
mock_krita.Extension = MagicMock
sys.modules["krita"] = mock_krita

mock_qt = MagicMock()
sys.modules["PyQt5"] = mock_qt
sys.modules["PyQt5.QtCore"] = MagicMock()
sys.modules["PyQt5.QtGui"] = MagicMock()

from kritamcp.snapshot_store import BatchSnapshotStore  # noqa: E402


@pytest.fixture
def store() -> BatchSnapshotStore:
    # Use a temporary directory for snapshots
    tmp_dir = tempfile.mkdtemp()
    store = BatchSnapshotStore(snapshot_dir=tmp_dir, max_snapshots=3)
    yield store
    # Cleanup
    shutil.rmtree(tmp_dir)


def test_create_and_get_snapshot(store: BatchSnapshotStore) -> None:
    # Create a dummy file
    snapshot_path = Path(store.snapshot_dir) / "test.png"
    snapshot_path.touch()

    batch_id = store.create_snapshot(["cmd1"], str(snapshot_path))
    assert batch_id is not None

    snapshot = store.get_snapshot(batch_id)
    assert snapshot is not None
    assert snapshot.canvas_before_path == str(snapshot_path)
    assert snapshot.commands == ["cmd1"]


def test_snapshot_eviction(store: BatchSnapshotStore) -> None:
    # Add 4 snapshots, max is 3
    paths = []
    ids = []
    for i in range(4):
        path = Path(store.snapshot_dir) / f"test_{i}.png"
        path.touch()
        paths.append(str(path))
        batch_id = store.create_snapshot([f"cmd_{i}"], str(path))
        ids.append(batch_id)

    # The first one (index 0) should be evicted
    assert store.get_snapshot(ids[0]) is None
    assert not Path(paths[0]).exists()

    # Others should still be there
    for i in range(1, 4):
        assert store.get_snapshot(ids[i]) is not None
        assert Path(paths[i]).exists()


def test_remove_snapshot(store: BatchSnapshotStore) -> None:
    path = Path(store.snapshot_dir) / "remove.png"
    path.touch()
    batch_id = store.create_snapshot([], str(path))

    assert path.exists()
    removed = store.remove_snapshot(batch_id)
    assert removed is True
    assert store.get_snapshot(batch_id) is None
    assert not path.exists()


def test_clear_store(store: BatchSnapshotStore) -> None:
    for i in range(3):
        path = Path(store.snapshot_dir) / f"clear_{i}.png"
        path.touch()
        store.create_snapshot([], str(path))

    store.clear()
    assert len(store._snapshots) == 0
    assert len(list(Path(store.snapshot_dir).iterdir())) == 0
