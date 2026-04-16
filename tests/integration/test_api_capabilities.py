"""Integration tests for Krita API version detection and capability gating."""

from __future__ import annotations

from typing import TYPE_CHECKING

from krita_client import ClientConfig, KritaClient

if TYPE_CHECKING:
    import pytest_httpx


class TestAPICapabilityDetection:
    """Tests for API capability detection and gating."""

    def test_get_capabilities_returns_krita_version(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Get capabilities should return Krita version info."""
        httpx_mock.add_response(
            json={
                "status": "ok",
                "capabilities": {
                    "select_ellipse": True,
                    "select_polygon": True,
                    "selection_bounds": True,
                    "krita_version": "5.2.0",
                },
                "selection_tools": ["select_ellipse", "select_polygon", "selection_bounds"],
                "unsupported_apis": None,
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.get_capabilities()
        assert result["status"] == "ok"
        assert "krita_version" in result.get("capabilities", {})

    def test_get_capabilities_returns_unsupported_guidance(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Get capabilities should return guidance for unsupported APIs."""
        httpx_mock.add_response(
            json={
                "status": "ok",
                "capabilities": {
                    "select_ellipse": False,
                    "select_polygon": False,
                    "selection_bounds": True,
                    "krita_version": "5.0.0",
                },
                "selection_tools": ["selection_bounds"],
                "unsupported_apis": {
                    "select_ellipse": {
                        "supported": False,
                        "message": "API 'select_ellipse' is not available in this Krita version",
                    },
                    "select_polygon": {
                        "supported": False,
                        "message": "API 'select_polygon' is not available in this Krita version",
                    },
                },
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.get_capabilities()
        assert result["status"] == "ok"
        unsupported = result.get("unsupported_apis")
        assert unsupported is not None
        assert "select_ellipse" in unsupported
        assert unsupported["select_ellipse"]["supported"] is False

    def test_select_ellipse_unavailable_returns_error(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Select ellipse should return error when API is unavailable."""
        httpx_mock.add_response(
            json={
                "status": "error",
                "supported": False,
                "message": (
                    "select_ellipse API is not available in this Krita version. "
                    "Please upgrade Krita or use select_rect instead."
                ),
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_ellipse(cx=50, cy=50, rx=30, ry=20)
        assert result["status"] == "error"
        assert result["supported"] is False
        assert "not available" in result["message"]

    def test_select_polygon_unavailable_returns_error(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Select polygon should return error when API is unavailable."""
        httpx_mock.add_response(
            json={
                "status": "error",
                "supported": False,
                "message": (
                    "select_polygon API is not available in this Krita version. "
                    "Please upgrade Krita or use select_rect instead."
                ),
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.select_polygon(points=[[0, 0], [100, 0], [50, 100]])
        assert result["status"] == "error"
        assert result["supported"] is False
        assert "not available" in result["message"]

    def test_selection_info_unavailable_bounds(self, httpx_mock: pytest_httpx.HTTPXMock) -> None:
        """Selection info should return guidance when bounds API is unavailable."""
        httpx_mock.add_response(
            json={
                "status": "ok",
                "has_selection": True,
                "bounds": None,
                "supported": False,
                "message": (
                    "selection_bounds API is not available in this Krita version. Upgrade to get selection bounds info."
                ),
            }
        )

        client = KritaClient(config=ClientConfig())
        result = client.selection_info()
        assert result["status"] == "ok"
        assert result["has_selection"] is True
        assert result["supported"] is False
        assert "not available" in result["message"]
