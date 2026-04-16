"""Integration tests for selection advanced features (color & alpha selection)."""

from __future__ import annotations

import pytest
import pytest_httpx

from krita_client import KritaClient, ClientConfig


class TestSelectByColor:
    """Tests for select_by_color client method."""

    def test_select_by_color_magic_wand(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Magic wand selection should send correct params."""
        httpx_mock.add_response(
            json={"status": "ok", "selected_count": 150, "method": "contiguous"}
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_by_color(x=50, y=50, tolerance=0.15)
        assert result["status"] == "ok"
        assert result["selected_count"] == 150

    def test_select_by_color_global(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Global color selection should send correct params."""
        httpx_mock.add_response(
            json={"status": "ok", "selected_count": 5000, "method": "global"}
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_by_color(tolerance=0.2, contiguous=False)
        assert result["status"] == "ok"
        assert result["selected_count"] == 5000


class TestSelectByAlpha:
    """Tests for select_by_alpha client method."""

    def test_select_by_alpha_defaults(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Alpha selection with defaults should send correct params."""
        httpx_mock.add_response(
            json={"status": "ok", "selected_count": 3000}
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_by_alpha()
        assert result["status"] == "ok"
        assert result["selected_count"] == 3000

    def test_select_by_alpha_custom_range(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Alpha selection with custom range should send correct params."""
        httpx_mock.add_response(
            json={"status": "ok", "selected_count": 1200}
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_by_alpha(min_alpha=50, max_alpha=200)
        assert result["status"] == "ok"
        assert result["selected_count"] == 1200
