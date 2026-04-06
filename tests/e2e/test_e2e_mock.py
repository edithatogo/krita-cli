"""E2E tests using mock Krita plugin server.

These tests verify the full stack (client → HTTP → mock plugin)
without requiring a real Krita instance. They run in CI by default.
"""

from __future__ import annotations

import json

from krita_client import KritaClient


class TestE2EHealth:
    """E2E health check tests."""

    def test_health_returns_ok(self, e2e_client: KritaClient) -> None:
        """Health check should return ok with plugin info."""
        result = e2e_client.health()
        assert result["status"] == "ok"
        assert result["plugin"] == "kritamcp"

    def test_health_includes_protocol_version(self, e2e_client: KritaClient) -> None:
        """Health check should include protocol version."""
        result = e2e_client.health()
        assert "protocol_version" in result


class TestE2ECanvas:
    """E2E canvas operation tests."""

    def test_new_canvas(self, e2e_client: KritaClient) -> None:
        """Creating a canvas should succeed."""
        result = e2e_client.new_canvas(width=100, height=100, name="Test")
        assert result["status"] == "ok"
        assert result["width"] == 100
        assert result["height"] == 100

    def test_get_canvas(self, e2e_client: KritaClient) -> None:
        """Exporting canvas should return a path."""
        result = e2e_client.get_canvas(filename="test.png")
        assert result["status"] == "ok"
        assert "path" in result


class TestE2ESelection:
    """E2E selection operation tests."""

    def test_select_rect(self, e2e_client: KritaClient) -> None:
        """Rectangular selection should succeed."""
        result = e2e_client.select_rect(x=10, y=20, width=100, height=200)
        assert result["status"] == "ok"
        assert result["x"] == 10
        assert result["y"] == 20

    def test_select_ellipse(self, e2e_client: KritaClient) -> None:
        """Elliptical selection should succeed."""
        result = e2e_client.select_ellipse(cx=50, cy=50, rx=30, ry=20)
        assert result["status"] == "ok"
        assert result["cx"] == 50

    def test_select_polygon(self, e2e_client: KritaClient) -> None:
        """Polygon selection should succeed."""
        points = [[0, 0], [100, 0], [50, 100]]
        result = e2e_client.select_polygon(points=points)
        assert result["status"] == "ok"
        assert len(result["points"]) == 3

    def test_selection_info_with_selection(self, e2e_client: KritaClient) -> None:
        """Selection info should report active selection after creating one."""
        e2e_client.select_rect(x=0, y=0, width=100, height=100)
        result = e2e_client.selection_info()
        assert result["has_selection"] is True

    def test_selection_info_no_selection(self, e2e_client: KritaClient) -> None:
        """Selection info should report no selection initially."""
        result = e2e_client.selection_info()
        assert result["has_selection"] is False

    def test_deselect(self, e2e_client: KritaClient) -> None:
        """Deselect should clear selection."""
        e2e_client.select_rect(x=0, y=0, width=100, height=100)
        result = e2e_client.deselect()
        assert result["status"] == "ok"

    def test_invert_selection(self, e2e_client: KritaClient) -> None:
        """Inverting selection should succeed."""
        e2e_client.select_rect(x=0, y=0, width=100, height=100)
        result = e2e_client.invert_selection()
        assert result["status"] == "ok"

    def test_clear_selection(self, e2e_client: KritaClient) -> None:
        """Clearing selection should succeed."""
        e2e_client.select_rect(x=0, y=0, width=100, height=100)
        result = e2e_client.clear_selection()
        assert result["status"] == "ok"


class TestE2EClippingAwareness:
    """E2E tests for clipping awareness in responses."""

    def test_stroke_without_selection_has_no_clipping(self, e2e_client: KritaClient) -> None:
        """Stroke without active selection should not include clipping notice."""
        result = e2e_client.stroke(points=[[0, 0], [100, 100]])
        assert result["status"] == "ok"
        assert "clipped_by_selection" not in result

    def test_stroke_with_selection_has_clipping_notice(self, e2e_client: KritaClient) -> None:
        """Stroke with active selection should include clipping notice."""
        e2e_client.select_rect(x=0, y=0, width=100, height=100)
        result = e2e_client.stroke(points=[[0, 0], [100, 100]])
        assert result["status"] == "ok"
        assert result.get("clipped_by_selection") is True


class TestE2EBatch:
    """E2E batch operation tests."""

    def test_batch_multiple_commands(self, e2e_client: KritaClient) -> None:
        """Batch with multiple commands should execute all."""
        commands = [
            {"action": "set_color", "params": {"color": "#ff0000"}},
            {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
        ]
        result = e2e_client.batch_execute(commands)
        assert result["status"] == "ok"
        assert len(result["results"]) == 2


class TestE2EHistory:
    """E2E command history tests."""

    def test_history_populated_after_operations(self, e2e_client: KritaClient) -> None:
        """Command history should be populated after operations."""
        e2e_client.new_canvas(width=100, height=100)
        e2e_client.set_color(color="#ff0000")
        result = e2e_client.get_command_history()
        assert result["status"] == "ok"
        assert result["count"] >= 2


class TestE2ECapabilities:
    """E2E capability detection tests."""

    def test_get_capabilities(self, e2e_client: KritaClient) -> None:
        """Capability detection should return available tools."""
        result = e2e_client.get_capabilities()
        assert result["status"] == "ok"
        assert "capabilities" in result
        assert "selection_tools" in result


class TestE2ESecurity:
    """E2E security status tests."""

    def test_get_security_status(self, e2e_client: KritaClient) -> None:
        """Security status should return limits and usage."""
        result = e2e_client.get_security_status()
        assert result["status"] == "ok"
        assert "rate_limit" in result
        assert "payload_limit" in result
