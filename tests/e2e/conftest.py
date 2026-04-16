"""End-to-end test harness with mock Krita plugin support.

This module provides fixtures and utilities for running E2E tests
both with a real Krita instance and with a mocked plugin server.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any, ClassVar

import pytest

from krita_client import ClientConfig, KritaClient

if TYPE_CHECKING:
    from collections.abc import Generator


class MockKritaPluginHandler(BaseHTTPRequestHandler):
    """Mock HTTP handler that simulates Krita plugin responses."""

    # Class-level state shared across requests
    _state: ClassVar[dict[str, Any]] = {
        "canvas_created": False,
        "canvas_width": 0,
        "canvas_height": 0,
        "color": "#1a1a2e",
        "strokes": [],
        "selection": None,
        "selection_history": [],  # For undo/redo of selection
        "history": [],
    }

    @classmethod
    def reset_state(cls) -> None:
        cls._state = {
            "canvas_created": False,
            "canvas_width": 0,
            "canvas_height": 0,
            "color": "#1a1a2e",
            "strokes": [],
            "selection": None,
            "selection_history": [],
            "history": [],
        }

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # Suppress log output during tests
        pass

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(
                {
                    "status": "ok",
                    "plugin": "kritamcp",
                    "protocol_version": "1.0.0",
                    "capabilities": {
                        "select_ellipse": True,
                        "select_polygon": True,
                        "selection_bounds": True,
                    },
                }
            )
        else:
            self._send_json({"error": "Unknown GET path"}, 404)

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        action = request.get("action", "")
        params = request.get("params", {})

        result = self._handle_action(action, params)
        self._send_json(result)

    def _handle_action(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Route actions to mock implementations."""
        self._state["history"].append({"action": action, "params": params})

        handlers = {
            "new_canvas": self._cmd_new_canvas,
            "set_color": self._cmd_set_color,
            "stroke": self._cmd_stroke,
            "fill": self._cmd_fill,
            "draw_shape": self._cmd_draw_shape,
            "get_canvas": self._cmd_get_canvas,
            "undo": self._cmd_undo,
            "redo": self._cmd_redo,
            "select_rect": self._cmd_select_rect,
            "select_ellipse": self._cmd_select_ellipse,
            "select_polygon": self._cmd_select_polygon,
            "selection_info": self._cmd_selection_info,
            "clear_selection": self._cmd_clear_selection,
            "invert_selection": self._cmd_invert_selection,
            "deselect": self._cmd_deselect,
            "select_by_color": self._cmd_select_by_color,
            "select_by_alpha": self._cmd_select_by_alpha,
            "batch": self._cmd_batch,
            "get_command_history": self._cmd_history,
            "get_capabilities": self._cmd_capabilities,
            "get_security_status": self._cmd_security_status,
        }

        handler = handlers.get(action)
        if handler is None:
            return {"status": "ok", "action": action, "mocked": True}
        return handler(params)

    def _cmd_new_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        self._state["canvas_created"] = True
        self._state["canvas_width"] = params.get("width", 800)
        self._state["canvas_height"] = params.get("height", 600)
        return {"status": "ok", "width": self._state["canvas_width"], "height": self._state["canvas_height"]}

    def _cmd_set_color(self, params: dict[str, Any]) -> dict[str, Any]:
        self._state["color"] = params.get("color", "#000000")
        return {"status": "ok"}

    def _cmd_stroke(self, params: dict[str, Any]) -> dict[str, Any]:
        points = params.get("points", [])
        if len(points) < 2:
            return {"error": "Need at least 2 points"}
        self._state["strokes"].append({"points": points, "color": self._state["color"]})
        result: dict[str, object] = {"status": "ok", "points_count": len(points)}
        if self._state["selection"]:
            result["clipped_by_selection"] = True
        return result

    def _cmd_fill(self, params: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, object] = {"status": "ok", "x": params.get("x", 0), "y": params.get("y", 0)}
        if self._state["selection"]:
            result["clipped_by_selection"] = True
        return result

    def _cmd_draw_shape(self, params: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, object] = {"status": "ok", "shape": params.get("shape", "unknown")}
        if self._state["selection"]:
            result["clipped_by_selection"] = True
        return result

    def _cmd_get_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ok", "path": "/tmp/mock_canvas.png"}

    def _cmd_select_rect(self, params: dict[str, Any]) -> dict[str, Any]:
        # Save to history before changing selection
        if self._state["selection"] is not None:
            self._state["selection_history"].append(self._state["selection"])
            # Clear redo stack when new action is performed
            self._state.setdefault("redo_stack", []).clear()
        self._state["selection"] = {"type": "rect", "params": params}
        return {
            "status": "ok",
            "x": params["x"],
            "y": params["y"],
            "width": params["width"],
            "height": params["height"],
        }

    def _cmd_select_ellipse(self, params: dict[str, Any]) -> dict[str, Any]:
        self._state["selection"] = {"type": "ellipse", "params": params}
        return {"status": "ok", "cx": params["cx"], "cy": params["cy"], "rx": params["rx"], "ry": params["ry"]}

    def _cmd_select_polygon(self, params: dict[str, Any]) -> dict[str, Any]:
        self._state["selection"] = {"type": "polygon", "params": params}
        return {"status": "ok", "points": params["points"]}

    def _cmd_selection_info(self, params: dict[str, Any]) -> dict[str, Any]:
        if self._state["selection"]:
            return {"status": "ok", "has_selection": True, "bounds": {"x": 0, "y": 0, "width": 100, "height": 100}}
        return {"status": "ok", "has_selection": False, "bounds": None}

    def _cmd_clear_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        self._state["selection"] = None
        return {"status": "ok"}

    def _cmd_invert_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        if self._state["selection"]:
            self._state["selection"]["inverted"] = not self._state["selection"].get("inverted", False)
        return {"status": "ok"}

    def _cmd_deselect(self, params: dict[str, Any]) -> dict[str, Any]:
        # Save to history before clearing (for undo)
        if self._state["selection"] is not None:
            self._state["selection_history"].append(self._state["selection"])
            # Clear redo stack when new action is performed
            self._state.setdefault("redo_stack", []).clear()
        self._state["selection"] = None
        return {"status": "ok"}

    def _cmd_undo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Undo the last selection operation."""
        if self._state["selection_history"]:
            # Save current state for redo
            self._state.setdefault("redo_stack", []).append(self._state["selection"])
            # Restore previous state
            self._state["selection"] = self._state["selection_history"].pop()
            return {"status": "ok", "undone": True}
        return {"status": "ok", "undone": False, "message": "Nothing to undo"}

    def _cmd_redo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Redo the last undone selection operation."""
        redo_stack = self._state.get("redo_stack", [])
        if redo_stack:
            # Save current state for undo
            self._state["selection_history"].append(self._state["selection"])
            # Restore redo state
            self._state["selection"] = redo_stack.pop()
            return {"status": "ok", "redone": True}
        return {"status": "ok", "redone": False, "message": "Nothing to redo"}

    def _cmd_batch(self, params: dict[str, Any]) -> dict[str, Any]:
        commands = params.get("commands", [])
        results = []
        for cmd in commands:
            action = cmd.get("action", "")
            cmd_params = cmd.get("params", {})
            result = self._handle_action(action, cmd_params)
            results.append({"action": action, "status": "ok" if "error" not in result else "error", "result": result})
        return {"status": "ok", "results": results, "count": len(results)}

    def _cmd_history(self, params: dict[str, Any]) -> dict[str, Any]:
        limit = params.get("limit", 20)
        return {"status": "ok", "history": self._state["history"][-limit:], "count": len(self._state["history"])}

    def _cmd_capabilities(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "capabilities": {"select_ellipse": True, "select_polygon": True, "selection_bounds": True},
            "selection_tools": ["select_ellipse", "select_polygon", "selection_bounds"],
        }

    def _cmd_security_status(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "rate_limit": {"max_commands_per_minute": 60, "window_seconds": 60.0, "current_usage": 0},
            "payload_limit": 10 * 1024 * 1024,
            "batch_size_limit": 50,
            "max_canvas_dim": 8192,
            "max_layers": 100,
        }

    def _cmd_select_by_color(self, params: dict[str, Any]) -> dict[str, Any]:
        """Mock select by color selection."""
        tolerance = params.get("tolerance", 0.1)
        contiguous = params.get("contiguous", True)
        x = params.get("x")
        y = params.get("y")

        method = "contiguous" if contiguous else "global"
        # Mock selected count based on tolerance
        selected_count = int(1000 * (1.0 - tolerance))

        result: dict[str, object] = {
            "status": "ok",
            "selected_count": selected_count,
            "method": method,
            "tolerance": tolerance,
        }
        if x is not None and y is not None:
            result["x"] = x
            result["y"] = y

        # Set selection state
        self._state["selection"] = {
            "type": "color",
            "params": params,
            "selected_count": selected_count,
        }
        return result

    def _cmd_select_by_alpha(self, params: dict[str, Any]) -> dict[str, Any]:
        """Mock select by alpha selection."""
        min_alpha = params.get("min_alpha", 1)
        max_alpha = params.get("max_alpha", 255)

        # Mock selected count based on alpha range
        range_size = max_alpha - min_alpha
        selected_count = int(5000 * (range_size / 255.0))

        result: dict[str, object] = {
            "status": "ok",
            "selected_count": selected_count,
            "min_alpha": min_alpha,
            "max_alpha": max_alpha,
        }

        # Set selection state
        self._state["selection"] = {
            "type": "alpha",
            "params": params,
            "selected_count": selected_count,
        }
        return result

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


@pytest.fixture
def mock_plugin_server() -> Generator[HTTPServer, None, None]:
    """Start a mock Krita plugin HTTP server for E2E testing."""
    MockKritaPluginHandler.reset_state()
    server = HTTPServer(("127.0.0.1", 0), MockKritaPluginHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.fixture
def e2e_client(mock_plugin_server: HTTPServer) -> KritaClient:
    """Create a KritaClient connected to the mock plugin server."""
    port = mock_plugin_server.server_address[1]
    config = ClientConfig(url=f"http://127.0.0.1:{port}")
    return KritaClient(config)
