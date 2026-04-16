"""Integration tests for selection persistence operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from krita_client import ClientConfig, KritaClient

if TYPE_CHECKING:
    import pytest_httpx


class TestSaveSelection:
    """Tests for save_selection client method."""

    def test_save_selection_defaults(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Save selection with default format."""
        httpx_mock.add_response(json={"status": "ok", "path": "/tmp/sel.png", "format": "png", "pixel_count": 5000})

        client = KritaClient(config=ClientConfig())
        result = client.save_selection(path="/tmp/sel.png")
        assert result["status"] == "ok"
        assert result["pixel_count"] == 5000

    def test_save_selection_custom_format(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Save selection with custom format."""
        httpx_mock.add_response(json={"status": "ok", "path": "/tmp/sel.bmp", "format": "bmp", "pixel_count": 5000})

        client = KritaClient(config=ClientConfig())
        result = client.save_selection(path="/tmp/sel.bmp", format="bmp")
        assert result["status"] == "ok"
        assert result["format"] == "bmp"


class TestLoadSelection:
    """Tests for load_selection client method."""

    def test_load_selection(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Load selection from file."""
        httpx_mock.add_response(json={"status": "ok", "path": "/tmp/sel.png", "loaded_pixels": 3000})

        client = KritaClient(config=ClientConfig())
        result = client.load_selection(path="/tmp/sel.png")
        assert result["status"] == "ok"
        assert result["loaded_pixels"] == 3000


class TestSelectionStats:
    """Tests for selection_stats client method."""

    def test_selection_stats_with_selection(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Get stats with active selection."""
        httpx_mock.add_response(
            json={
                "status": "ok",
                "has_selection": True,
                "pixel_count": 15000,
                "area_percentage": 23.5,
                "centroid": {"x": 250.5, "y": 180.3},
                "bounds": {"x": 100, "y": 50, "width": 200, "height": 150},
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.selection_stats()
        assert result["status"] == "ok"
        assert result["has_selection"] is True
        assert result["pixel_count"] == 15000
        assert result["area_percentage"] == 23.5

    def test_selection_stats_no_selection(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Get stats with no selection."""
        httpx_mock.add_response(json={"status": "ok", "has_selection": False, "pixel_count": 0})

        client = KritaClient(config=ClientConfig())
        result = client.selection_stats()
        assert result["status"] == "ok"
        assert result["has_selection"] is False
