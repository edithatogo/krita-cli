"""End-to-end tests against a real running Krita instance.

These tests launch Krita automatically via KritaDriver, install the
kritamcp plugin, open a canvas, and exercise the full stack.

Run with:
    uv run pytest tests/e2e/test_krita_live.py -m e2e -v

Requirements:
  - Krita installed (discovered via scoop, PATH, or common locations)
  - pywinauto  (pip install pywinauto)
  - Windows (pywinauto is Windows-only; tests are skipped on other platforms)
"""

from __future__ import annotations

import sys

import pytest

from krita_client import KritaClient

# All tests in this file require a live Krita instance
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


@pytest.mark.skipif(sys.platform != "win32", reason="Live Krita tests require Windows")
class TestLivePlugin:
    """Verify the plugin loads and the HTTP server starts."""

    def test_health(self, live_client: KritaClient) -> None:
        result = live_client.health()
        assert result["status"] == "ok"
        assert result["plugin"] == "kritamcp"

    def test_info_has_commands(self, live_client: KritaClient, krita_plugin_base_url: str) -> None:
        import os

        import httpx

        os.environ.pop("SSL_CERT_FILE", None)
        r = httpx.get(f"{krita_plugin_base_url}/info", timeout=5)
        info = r.json()
        assert "commands" in info
        assert len(info["commands"]) > 0

    def test_capabilities(self, live_client: KritaClient) -> None:
        result = live_client.call("get_capabilities", {})
        assert result["status"] == "ok"
        assert "capabilities" in result


@pytest.mark.skipif(sys.platform != "win32", reason="Live Krita tests require Windows")
class TestLiveCanvas:
    """Verify canvas creation and basic painting commands."""

    def test_new_canvas(self, live_client: KritaClient) -> None:
        result = live_client.new_canvas(width=400, height=400, name="E2E Test Canvas")
        assert result["status"] == "ok"

    def test_set_color(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=400, height=400, name="E2E Color Test")
        result = live_client.set_color(color="#ff6600")
        assert result["status"] == "ok"

    def test_stroke(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=400, height=400, name="E2E Stroke Test")
        live_client.set_color(color="#0066ff")
        result = live_client.stroke(points=[[50, 50], [200, 200], [350, 50]])
        assert result["status"] == "ok"

    def test_fill(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=400, height=400, name="E2E Fill Test")
        live_client.set_color(color="#00cc44")
        result = live_client.fill(x=200, y=200, radius=80)
        assert result["status"] == "ok"

    def test_get_canvas_exports_file(self, live_client: KritaClient) -> None:
        import os

        live_client.new_canvas(width=200, height=200, name="E2E Export Test")
        result = live_client.get_canvas(filename="e2e_export.png")
        assert result["status"] == "ok"
        assert "path" in result
        assert os.path.exists(result["path"])


@pytest.mark.skipif(sys.platform != "win32", reason="Live Krita tests require Windows")
class TestLiveBatch:
    """Verify batch command execution against real Krita."""

    def test_batch_paint_sequence(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=400, height=400, name="E2E Batch Test")
        commands = [
            {"action": "set_color", "params": {"color": "#ff0000"}},
            {"action": "stroke", "params": {"points": [[10, 10], [200, 200]]}},
            {"action": "set_color", "params": {"color": "#0000ff"}},
            {"action": "fill", "params": {"x": 300, "y": 300, "radius": 60}},
        ]
        result = live_client.batch_execute(commands)
        assert result["status"] == "ok"
        assert result["count"] == len(commands)
        for item in result["results"]:
            assert item["status"] == "ok", f"Command {item['action']} failed: {item}"


@pytest.mark.skipif(sys.platform != "win32", reason="Live Krita tests require Windows")
class TestLiveLayers:
    """Verify layer management commands against real Krita."""

    def test_list_layers(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=200, height=200, name="E2E Layers Test")
        result = live_client.list_layers()
        assert result["status"] == "ok"
        assert isinstance(result.get("layers"), list)

    def test_create_and_select_layer(self, live_client: KritaClient) -> None:
        live_client.new_canvas(width=200, height=200, name="E2E Layer Create")
        result = live_client.create_layer(name="Test Layer")
        assert result["status"] == "ok"
