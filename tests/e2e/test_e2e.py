"""End-to-end tests requiring a running Krita instance.

These tests are skipped by default since they require Krita with the
MCP plugin to be running. Run with: pytest tests/e2e/ -m e2e
"""

from __future__ import annotations

import pytest

from krita_client import KritaClient, KritaConnectionError


@pytest.mark.e2e
def test_e2e_health() -> None:
    """Test health check against a real Krita instance."""
    client = KritaClient()
    try:
        result = client.health()
        assert result.get("status") == "ok"
        assert result.get("plugin") == "kritamcp"
    except KritaConnectionError:
        pytest.skip("Krita is not running with the MCP plugin")


@pytest.mark.e2e
def test_e2e_new_canvas_and_export() -> None:
    """Test creating a canvas and exporting it."""
    client = KritaClient()
    try:
        result = client.new_canvas(width=100, height=100, name="E2E Test")
        assert result.get("status") == "ok"

        result = client.get_canvas(filename="e2e_test.png")
        assert result.get("status") == "ok"
        assert "path" in result
    except KritaConnectionError:
        pytest.skip("Krita is not running with the MCP plugin")


@pytest.mark.e2e
def test_e2e_set_color_and_stroke() -> None:
    """Test setting color and drawing a stroke."""
    client = KritaClient()
    try:
        client.new_canvas(width=200, height=200, name="E2E Stroke Test")
        result = client.set_color(color="#ff0000")
        assert result.get("status") == "ok"

        result = client.stroke(points=[[10, 10], [100, 100], [190, 10]])
        assert result.get("status") == "ok"
    except KritaConnectionError:
        pytest.skip("Krita is not running with the MCP plugin")


@pytest.mark.e2e
def test_e2e_batch_operations() -> None:
    """Test batch command execution."""
    client = KritaClient()
    try:
        client.new_canvas(width=200, height=200, name="E2E Batch Test")
        commands = [
            {"action": "set_color", "params": {"color": "#00ff00"}},
            {"action": "fill", "params": {"x": 100, "y": 100, "radius": 50}},
        ]
        result = client.batch(commands)
        assert result.get("status") == "ok"
    except KritaConnectionError:
        pytest.skip("Krita is not running with the MCP plugin")
