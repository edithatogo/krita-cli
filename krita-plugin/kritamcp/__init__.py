"""
Krita MCP Bridge — HTTP server for external paint commands in Krita.
Allows Claude (or any MCP client) to paint by sending commands to this plugin.

Fixes applied:
- Race condition: per-command threading.Condition replaces shared Event
- Thread safety: itertools.count for command IDs
- OOM prevention: dimension limits on new_canvas/clear
- Path sanitization: traversal prevention in save/open_file
- API mismatch: pressure parameter mapped to hardness/opacity
- Graceful shutdown: teardown() method
- Protocol version in /health endpoint
- Clean imports, error logging, numpy-accelerated rendering (optional)
"""

from __future__ import annotations

import itertools
import json
import logging
import math
import os
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

try:
    with open(os.path.expanduser("~/kritamcp_startup.log"), "a") as _f:
        import datetime as _dt

        _f.write(f"[{_dt.datetime.now().isoformat()}] kritamcp import begin as {__name__} (Python {sys.version})\n")
except Exception:
    pass

from krita import *
from PyQt5.QtCore import QThread, QTimer, QPoint
from PyQt5.QtGui import QColor, QPolygon

from kritamcp.history_store import CommandHistoryStore
from kritamcp.payload_validator import validate_payload_size, MAX_PAYLOAD_SIZE
from kritamcp.rate_limiter import RateLimiter
from kritamcp.snapshot_store import BatchSnapshotStore

# -- Startup diagnostics (file log so failures are visible outside Krita) ----
_DIAG_LOG = os.path.expanduser("~/kritamcp_startup.log")


def _log_diag(message: str) -> None:
    try:
        with open(_DIAG_LOG, "a") as _f:
            import datetime as _dt

            _f.write(f"[{_dt.datetime.now().isoformat()}] {message}\n")
    except Exception:
        pass


def _expand_user_path(path: str) -> str:
    """Expand user and environment markers in a filesystem path."""
    return os.path.expandvars(os.path.expanduser(path))


try:
    _log_diag(f"kritamcp module loaded as {__name__} (Python {sys.version})")
except Exception:
    pass

# Try to import numpy for accelerated rendering
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# -- Configuration -----------------------------------------------------------

SERVER_PORT = 5678
CANVAS_OUTPUT_DIR = os.path.expanduser("~/krita-mcp-output")
MAX_CANVAS_DIM = 8192
MAX_BATCH_SIZE = 50
MAX_LAYERS = 100
PLUGIN_VERSION = "0.2.0"
PROTOCOL_VERSION = "1.0.0"

logger = logging.getLogger("kritamcp")


def make_error(message: str, code: str = "INTERNAL_ERROR", recoverable: bool = True) -> dict[str, Any]:
    msg = message
    cd = code
    recov = recoverable

    if cd == "INTERNAL_ERROR" and code == "INTERNAL_ERROR":
        if "No active" in message and "document" in message.lower():
            cd = "NO_ACTIVE_DOCUMENT"
        elif "No active" in message and "layer" in message.lower():
            cd = "NO_ACTIVE_LAYER"
        elif "No active" in message and "view" in message.lower():
            cd = "NO_ACTIVE_VIEW"
        elif "layer" in message.lower() and ("not found" in message.lower() or "no active" in message.lower()):
            cd = "LAYER_NOT_FOUND"
        elif "bounds" in message.lower() or "dimensions" in message.lower() or "positive" in message.lower():
            cd = "INVALID_PARAMETERS"
        elif "not found" in message.lower() or "Unknown" in message:
            cd = "FILE_NOT_FOUND"
        elif "timeout" in message.lower():
            cd = "COMMAND_TIMEOUT"
        elif "shape" in message.lower() and ("not supported" in message.lower() or "invalid" in message.lower()):
            cd = "INVALID_SHAPE"
        elif "brush" in message.lower() and ("not found" in message.lower()):
            cd = "BRUSH_NOT_FOUND"
        elif "color" in message.lower() and ("invalid" in message.lower()):
            cd = "INVALID_COLOR"
        elif "too large" in message.lower() or "exceed" in message.lower():
            cd = "CANVAS_TOO_LARGE"
        elif "traversal" in message.lower():
            cd = "PATH_TRAVERSAL_BLOCKED"
        elif "file not found" in message.lower():
            cd = "FILE_NOT_FOUND"

    return {"error": {"code": cd, "message": msg, "recoverable": recov}}


# -- Thread-safe command queue -----------------------------------------------


class CommandQueue:
    """Thread-safe command queue with per-command condition variables.

    Fixes the race condition from the original implementation that used a
    single shared threading.Event for all commands, which could cause lost
    signals when multiple commands were queued simultaneously.
    """

    def __init__(self) -> None:
        self._queue: list[tuple[int, dict[str, Any]]] = []
        self._results: dict[int, dict[str, Any]] = {}
        self._conditions: dict[int, threading.Condition] = {}
        self._lock = threading.Lock()

    def push(self, command_id: int, command: dict[str, Any]) -> None:
        with self._lock:
            self._queue.append((command_id, command))

    def pop(self) -> tuple[int, dict[str, Any]] | None:
        with self._lock:
            if self._queue:
                return self._queue.pop(0)
            return None

    def set_result(self, command_id: int, result: dict[str, Any]) -> None:
        with self._lock:
            self._results[command_id] = result
            condition = self._conditions.pop(command_id, None)
        if condition is not None:
            with condition:
                condition.notify_all()

    def get_result(self, command_id: int, timeout: float = 120.0) -> dict[str, Any]:
        """Wait for result with timeout using per-command condition variable."""
        condition = threading.Condition()
        with self._lock:
            if command_id in self._results:
                return self._results.pop(command_id)
            self._conditions[command_id] = condition

        with condition:
            condition.wait(timeout=timeout)

        with self._lock:
            if command_id in self._results:
                return self._results.pop(command_id)

        return make_error("Timeout waiting for command execution", code="COMMAND_TIMEOUT", recoverable=True)


# -- Rate limiter ------------------------------------------------------------


# Global command queue and thread-safe counter
command_queue = CommandQueue()
_command_counter = itertools.count(1)
rate_limiter = RateLimiter()
history_store = CommandHistoryStore(max_size=100)


def _next_command_id() -> int:
    return next(_command_counter)


# -- HTTP request handler ----------------------------------------------------


class PaintRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for paint commands."""

    def log_message(self, format: str, *args: Any) -> None:
        logger.debug(format, *args)

    def send_json_response(self, data: dict[str, Any], status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self) -> None:
        """Handle GET requests — health check and info."""
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self.send_json_response(
                {
                    "status": "ok",
                    "plugin": "kritamcp",
                    "version": PLUGIN_VERSION,
                    "protocol_version": PROTOCOL_VERSION,
                }
            )
        elif parsed.path == "/info":
            self.send_json_response(
                {
                    "status": "ok",
                    "version": PLUGIN_VERSION,
                    "protocol_version": PROTOCOL_VERSION,
                    "canvas_dir": CANVAS_OUTPUT_DIR,
                    "commands": [
                        "new_canvas",
                        "set_color",
                        "set_brush",
                        "stroke",
                        "fill",
                        "draw_shape",
                        "get_canvas",
                        "undo",
                        "redo",
                        "clear",
                        "save",
                        "get_color_at",
                        "list_brushes",
                        "open_file",
                        "batch",
                    ],
                }
            )
        else:
            self.send_json_response(make_error("Unknown endpoint", code="UNKNOWN_ACTION", recoverable=False), 404)

    def do_POST(self) -> None:
        """Handle POST requests — paint commands."""
        # SECURITY: Check rate limit before processing any command
        if not rate_limiter.allow():
            self.send_json_response(
                make_error(
                    f"Rate limit exceeded. Max {rate_limiter.max_commands} commands per minute.",
                    code="RATE_LIMIT_EXCEEDED",
                    recoverable=True,
                ),
                429,
            )
            return

        content_length = int(self.headers.get("Content-Length", 0))

        # SECURITY: Validate payload size
        payload_error = validate_payload_size(content_length)
        if payload_error:
            self.send_json_response(make_error(payload_error, code="PAYLOAD_TOO_LARGE", recoverable=True), 413)
            return

        body = self.rfile.read(content_length).decode("utf-8")

        try:
            command = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_response(make_error("Invalid JSON", code="INVALID_PARAMETERS", recoverable=False), 400)
            return

        # SECURITY: Validate batch size before processing
        if command.get("action") == "batch":
            params = command.get("params", {})
            commands = params.get("commands", [])
            if len(commands) > MAX_BATCH_SIZE:
                self.send_json_response(
                    make_error(
                        f"Batch size exceeds maximum of {MAX_BATCH_SIZE} commands.",
                        code="BATCH_SIZE_EXCEEDED",
                        recoverable=True,
                    ),
                    400,
                )
                return

        command_id = _next_command_id()
        command_queue.push(command_id, command)
        result = command_queue.get_result(command_id)

        if "error" in result:
            self.send_json_response(result, 500)
        else:
            self.send_json_response(result)


# -- Server thread -----------------------------------------------------------


class ServerThread(QThread):
    """Thread to run HTTP server without blocking Krita UI."""

    def __init__(self, port: int) -> None:
        super().__init__()
        self.port = port
        self.server: HTTPServer | None = None

    def run(self) -> None:
        try:
            _log_diag(f"HTTP server thread starting on port {self.port}")
            self.server = ThreadingHTTPServer(("localhost", self.port), PaintRequestHandler)
            logger.info("HTTP server started on port %d", self.port)
            _log_diag(f"HTTP server started on port {self.port}")
            self.server.serve_forever()
        except OSError as exc:
            logger.error("Failed to start HTTP server on port %d: %s", self.port, exc)
            _log_diag(f"HTTP server failed on port {self.port}: {exc}")

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            logger.info("HTTP server stopped")


# -- Krita extension ---------------------------------------------------------


class KritaMCPExtension(Extension):
    """Main Krita extension class."""

    def __init__(self, parent: Any) -> None:
        _log_diag("KritaMCPExtension.__init__ begin")
        super().__init__(parent)
        self.server_thread: ServerThread | None = None
        self.timer: QTimer | None = None
        self.current_brush_size: int = 20
        self.current_opacity: float = 1.0
        self.snapshot_store = BatchSnapshotStore()

        # API capability detection
        self._api_capabilities: dict[str, bool] = self._detect_capabilities()

        # Load configuration
        self.config_path = os.path.expanduser("~/.kritamcp_config.json")
        self.load_config()
        _log_diag("KritaMCPExtension.__init__ after load_config")
        self._ensure_runtime_started()
        _log_diag("KritaMCPExtension.__init__ end")

    def _detect_capabilities(self) -> dict[str, bool]:
        """Detect which selection APIs are available in this Krita version."""
        capabilities: dict[str, bool] = {}
        try:
            from krita import Document

            doc: Document | None = None
            # Test on a temporary document if available, otherwise infer from API
            # Check if Selection.selectEllipse exists
            sel = None
            if doc:
                sel = doc.selection()
            if sel and hasattr(sel, "selectEllipse"):
                capabilities["select_ellipse"] = True
            else:
                capabilities["select_ellipse"] = False
            if sel and hasattr(sel, "selectPolygon"):
                capabilities["select_polygon"] = True
            else:
                capabilities["select_polygon"] = False
            if sel and hasattr(sel, "bounds"):
                capabilities["selection_bounds"] = True
            else:
                capabilities["selection_bounds"] = False
        except Exception:
            capabilities["select_ellipse"] = False
            capabilities["select_polygon"] = False
            capabilities["selection_bounds"] = False

        # Add Krita API version info
        try:
            from krita import Krita

            krita_instance = Krita.instance()
            krita_version_str = krita_instance.version() if krita_instance else Krita.version()
            capabilities["krita_version"] = krita_version_str
        except (AttributeError, ImportError, TypeError):
            capabilities["krita_version"] = "unknown"

        return capabilities

    def get_capabilities(self) -> dict[str, object]:
        """Return detected API capabilities."""
        # Build list of unsupported APIs with guidance
        unsupported_guidance = {}
        for api_name, available in self._api_capabilities.items():
            if not available and api_name != "krita_version":
                unsupported_guidance[api_name] = {
                    "supported": False,
                    "message": f"API '{api_name}' is not available in this Krita version",
                }

        return {
            "status": "ok",
            "capabilities": self._api_capabilities,
            "selection_tools": [
                name for name, available in self._api_capabilities.items() if available and name != "krita_version"
            ],
            "unsupported_apis": unsupported_guidance if unsupported_guidance else None,
        }

    def load_config(self) -> None:
        """Load configuration from ~/.krita-cli/config.json first, then fallback to ~/.kritamcp_config.json."""
        global SERVER_PORT, CANVAS_OUTPUT_DIR, MAX_CANVAS_DIM, MAX_BATCH_SIZE, MAX_LAYERS
        # Try the new krita-cli config location first
        krita_cli_config = os.path.expanduser("~/.krita-cli/config.json")
        if os.path.exists(krita_cli_config):
            try:
                with open(krita_cli_config, encoding="utf-8") as f:
                    config = json.load(f)
                    SERVER_PORT = config.get("port", SERVER_PORT)
                    CANVAS_OUTPUT_DIR = _expand_user_path(config.get("canvas_output_dir", CANVAS_OUTPUT_DIR))
                    MAX_CANVAS_DIM = config.get("max_canvas_dim", MAX_CANVAS_DIM)
                    MAX_BATCH_SIZE = config.get("max_batch_size", MAX_BATCH_SIZE)
                    MAX_LAYERS = config.get("max_layers", MAX_LAYERS)
                    rate_limiter.max_commands = config.get("max_commands_per_minute", rate_limiter.max_commands)
                    logger.info("Loaded config from %s", krita_cli_config)
                    return
            except Exception as e:
                logger.error("Failed to load config from %s: %s", krita_cli_config, e)
        # Fallback to legacy config path
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    config = json.load(f)
                    SERVER_PORT = config.get("port", SERVER_PORT)
                    CANVAS_OUTPUT_DIR = _expand_user_path(config.get("output_dir", CANVAS_OUTPUT_DIR))
                    MAX_CANVAS_DIM = config.get("max_canvas_dim", MAX_CANVAS_DIM)
                    logger.info("Loaded config from %s", self.config_path)
            except Exception as e:
                logger.error("Failed to load config from %s: %s", self.config_path, e)

    def setup(self) -> None:
        self._ensure_runtime_started()

    def createActions(self, window: Any) -> None:
        """Called when a new window is created."""
        self._ensure_runtime_started()

    def call(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Backward-compatible generic dispatcher used by the live tests."""
        return self.handle_command(action, params or {})

    def _ensure_runtime_started(self) -> None:
        """Start background runtime pieces once, regardless of Krita's callback order."""
        os.makedirs(CANVAS_OUTPUT_DIR, exist_ok=True)

        if self.server_thread is None:
            _log_diag(f"Requested HTTP server startup on port {SERVER_PORT}")
            self.server_thread = ServerThread(SERVER_PORT)
            self.server_thread.start()

        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_commands)
            self.timer.start(50)

    def teardown(self) -> None:
        """Graceful shutdown when Krita exits."""
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None
        logger.info("KritaMCP extension shut down")

    def process_commands(self) -> None:
        """Process commands from queue in main thread."""
        item = command_queue.pop()
        if item is None:
            return

        command_id, command = item
        try:
            result = self.execute_command(command)
        except Exception as exc:
            logger.exception("Error executing command %s", command.get("action"))
            result = make_error(str(exc))
        command_queue.set_result(command_id, result)

    def execute_command(self, command: dict[str, Any]) -> dict[str, Any]:
        """Execute a paint command and return result."""
        import time

        action = command.get("action")
        params = command.get("params", {})

        handlers = {
            "new_canvas": self.cmd_new_canvas,
            "set_color": self.cmd_set_color,
            "set_brush": self.cmd_set_brush,
            "stroke": self.cmd_stroke,
            "fill": self.cmd_fill,
            "draw_shape": self.cmd_draw_shape,
            "get_canvas": self.cmd_get_canvas,
            "undo": self.cmd_undo,
            "redo": self.cmd_redo,
            "clear": self.cmd_clear,
            "save": self.cmd_save,
            "get_color_at": self.cmd_get_color_at,
            "list_brushes": self.cmd_list_brushes,
            "open_file": self.cmd_open_file,
            "batch": self.cmd_batch,
            "get_canvas_info": self.cmd_get_canvas_info,
            "get_current_color": self.cmd_get_current_color,
            "get_current_brush": self.cmd_get_current_brush,
            "list_layers": self.cmd_list_layers,
            "create_layer": self.cmd_create_layer,
            "select_layer": self.cmd_select_layer,
            "delete_layer": self.cmd_delete_layer,
            "rename_layer": self.cmd_rename_layer,
            "set_layer_opacity": self.cmd_set_layer_opacity,
            "set_layer_visibility": self.cmd_set_layer_visibility,
            "select_rect": self.cmd_select_rect,
            "select_ellipse": self.cmd_select_ellipse,
            "select_polygon": self.cmd_select_polygon,
            "selection_info": self.cmd_selection_info,
            "get_capabilities": self.cmd_get_capabilities,
            "get_security_status": self.cmd_get_security_status,
            "transform_selection": self.cmd_transform_selection,
            "grow_selection": self.cmd_grow_selection,
            "shrink_selection": self.cmd_shrink_selection,
            "border_selection": self.cmd_border_selection,
            "combine_selections": self.cmd_combine_selections,
            "select_area": self.cmd_select_area,
            "clear_selection": self.cmd_clear_selection,
            "fill_selection": self.cmd_fill_selection,
            "deselect": self.cmd_deselect,
            "invert_selection": self.cmd_invert_selection,
            "select_by_color": self.cmd_select_by_color,
            "select_by_alpha": self.cmd_select_by_alpha,
            "save_selection": self.cmd_save_selection,
            "load_selection": self.cmd_load_selection,
            "selection_stats": self.cmd_selection_stats,
            "save_selection_channel": self.cmd_save_selection_channel,
            "load_selection_channel": self.cmd_load_selection_channel,
            "list_selection_channels": self.cmd_list_selection_channels,
            "delete_selection_channel": self.cmd_delete_selection_channel,
            "get_command_history": self.cmd_get_command_history,
            "rollback": self.cmd_rollback,
        }

        handler = handlers.get(action)
        if handler is None:
            return make_error(f"Unknown action: {action}", code="UNKNOWN_ACTION", recoverable=False)

        start = time.monotonic()
        result = handler(params)
        duration_ms = (time.monotonic() - start) * 1000

        # Record command in history (skip history queries to avoid recursion)
        if action != "get_command_history":
            status = "error" if "error" in result else "ok"
            history_store.add(
                {
                    "action": action,
                    "params": params,
                    "timestamp": time.time(),
                    "status": status,
                    "duration_ms": round(duration_ms, 2),
                    "error": result.get("error", {}).get("message") if status == "error" else None,
                }
            )

        return result

    # -- Canvas & State Introspection -----------------------------------------

    def cmd_get_canvas_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get information about the current canvas."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)
        return {
            "status": "ok",
            "name": doc.name(),
            "width": doc.width(),
            "height": doc.height(),
            "color_model": doc.colorModel(),
            "color_depth": doc.colorDepth(),
            "resolution": doc.resolution(),
        }

    def cmd_get_current_color(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get the current foreground and background colors."""
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        fg = view.foregroundColor()
        bg = view.backgroundColor()
        canvas = view.canvas()

        fg_q = fg.colorForCanvas(canvas)
        bg_q = bg.colorForCanvas(canvas)

        return {
            "status": "ok",
            "foreground": fg_q.name(),
            "background": bg_q.name(),
        }

    def cmd_get_current_brush(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get the current brush preset and properties."""
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        preset = view.brushPreset()
        return {
            "status": "ok",
            "preset": preset.name() if preset else "unknown",
            "size": view.brushSize(),
            "opacity": view.brushOpacity(),
        }

    # -- Layer Management -----------------------------------------------------

    def _get_all_nodes(self, parent: Node) -> list[Node]:
        """Recursively collect all nodes."""
        nodes = []
        for child in parent.childNodes():
            nodes.append(child)
            nodes.extend(self._get_all_nodes(child))
        return nodes

    def cmd_list_layers(self, params: dict[str, Any]) -> dict[str, Any]:
        """List all layers in the document."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        all_nodes = self._get_all_nodes(doc.rootNode())
        layers = []
        for node in all_nodes:
            layers.append(
                {
                    "name": node.name(),
                    "type": node.type(),
                    "visible": node.visible(),
                    "opacity": node.opacity() / 255.0 if node.opacity() > 1.0 else node.opacity(),
                    "locked": node.locked(),
                }
            )
        return {"status": "ok", "layers": layers, "count": len(layers)}

    def cmd_create_layer(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new layer."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        name = params.get("name", "New Layer")
        layer_type = params.get("layer_type", "paintlayer")

        # SECURITY: limit layers to prevent resource exhaustion
        all_nodes = self._get_all_nodes(doc.rootNode())
        if len(all_nodes) >= MAX_LAYERS:
            return make_error(
                f"Maximum layer count exceeded ({MAX_LAYERS})",
                code="LAYER_LIMIT_EXCEEDED",
                recoverable=True,
            )

        layer = doc.createNode(name, layer_type)
        doc.rootNode().addChildNode(layer, None)
        return {"status": "ok", "name": name, "type": layer_type}

    def _find_node(self, name: str) -> Node | None:
        """Find a node by name in the active document."""
        doc = self.get_active_document()
        if not doc:
            return None
        all_nodes = self._get_all_nodes(doc.rootNode())
        for node in all_nodes:
            if node.name() == name:
                return node
        return None

    def cmd_select_layer(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select a layer by name."""
        name = params.get("name")
        if not name:
            return make_error("Missing layer name", code="INVALID_PARAMETERS", recoverable=True)

        node = self._find_node(name)
        if not node:
            return make_error(f"Layer not found: {name}", code="LAYER_NOT_FOUND", recoverable=True)

        doc = self.get_active_document()
        doc.setActiveNode(node)
        return {"status": "ok", "name": name}

    def cmd_delete_layer(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a layer by name."""
        name = params.get("name")
        node = self._find_node(name)
        if not node:
            return make_error(f"Layer not found: {name}", code="LAYER_NOT_FOUND", recoverable=True)

        doc = self.get_active_document()
        doc.removeNode(node)
        return {"status": "ok", "name": name}

    def cmd_rename_layer(self, params: dict[str, Any]) -> dict[str, Any]:
        """Rename a layer."""
        old_name = params.get("old_name")
        new_name = params.get("new_name")
        node = self._find_node(old_name)
        if not node:
            return make_error(f"Layer not found: {old_name}", code="LAYER_NOT_FOUND", recoverable=True)

        node.setName(new_name)
        return {"status": "ok", "old_name": old_name, "new_name": new_name}

    def cmd_set_layer_opacity(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set layer opacity."""
        name = params.get("name")
        opacity = params.get("opacity", 1.0)
        node = self._find_node(name)
        if not node:
            return make_error(f"Layer not found: {name}", code="LAYER_NOT_FOUND", recoverable=True)

        # Krita uses 0-255 for opacity internally but python API often takes float or int.
        # According to stubs, it takes float.
        node.setOpacity(opacity)
        return {"status": "ok", "name": name, "opacity": opacity}

    def cmd_set_layer_visibility(self, params: dict[str, Any]) -> dict[str, Any]:
        """Toggle layer visibility."""
        name = params.get("name")
        visible = params.get("visible", True)
        node = self._find_node(name)
        if not node:
            return make_error(f"Layer not found: {name}", code="LAYER_NOT_FOUND", recoverable=True)

        node.setVisible(visible)
        return {"status": "ok", "name": name, "visible": visible}

    # -- Selection Tools ------------------------------------------------------

    def cmd_select_area(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select a rectangular area."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        x = params.get("x", 0)
        y = params.get("y", 0)
        w = params.get("width", 100)
        h = params.get("height", 100)

        if w < 1 or h < 1 or x < 0 or y < 0:
            return make_error("Invalid selection dimensions", code="INVALID_PARAMETERS", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error(
                "Selection API not available in this Krita version", code="INTERNAL_ERROR", recoverable=False
            )

        selection.select(x, y, w, h, 255)
        doc.refreshProjection()
        # Wrap in transaction for undo support
        try:
            doc.startTransaction("Select Rectangle")
            doc.endTransaction()
        except (AttributeError, TypeError):
            pass  # Transaction API not available
        return {"status": "ok", "x": x, "y": y, "width": w, "height": h}

    def cmd_select_rect(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select a rectangular area (alias for select_area with validated params)."""
        return self.cmd_select_area(params)

    def cmd_select_ellipse(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select an elliptical area."""
        # Check API availability
        if not self._api_capabilities.get("select_ellipse", False):
            return {
                "status": "error",
                "supported": False,
                "message": "select_ellipse API is not available in this Krita version. Please upgrade Krita or use select_rect instead.",
            }

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        cx = params.get("cx", 0)
        cy = params.get("cy", 0)
        rx = params.get("rx", 50)
        ry = params.get("ry", 50)

        if rx < 1 or ry < 1:
            return make_error("Invalid ellipse dimensions", code="INVALID_PARAMETERS", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error(
                "Selection API not available in this Krita version", code="INTERNAL_ERROR", recoverable=False
            )

        try:
            selection.selectEllipse(cx - rx, cy - ry, rx * 2, ry * 2, 255)
        except AttributeError:
            # Fallback: use rectangular select for older Krita versions without selectEllipse
            selection.select(cx - rx, cy - ry, rx * 2, ry * 2, 255)

        doc.refreshProjection()
        return {"status": "ok", "cx": cx, "cy": cy, "rx": rx, "ry": ry}

    def cmd_select_polygon(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select a polygonal area."""
        # Check API availability
        if not self._api_capabilities.get("select_polygon", False):
            return {
                "status": "error",
                "supported": False,
                "message": "select_polygon API is not available in this Krita version. Please upgrade Krita or use select_rect instead.",
            }

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        points = params.get("points", [])
        if len(points) < 3:
            return make_error("Polygon requires at least 3 points", code="INVALID_PARAMETERS", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error(
                "Selection API not available in this Krita version", code="INTERNAL_ERROR", recoverable=False
            )

        polygon = QPolygon([QPoint(int(p[0]), int(p[1])) for p in points])
        selection.selectPolygon(polygon, 255)
        doc.refreshProjection()
        return {"status": "ok", "points": points}

    def cmd_selection_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get information about the current selection."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return {"status": "ok", "has_selection": False, "bounds": None}

        # Check if bounds() API is available
        if not self._api_capabilities.get("selection_bounds", False):
            return {
                "status": "ok",
                "has_selection": True,
                "bounds": None,
                "supported": False,
                "message": "selection_bounds API is not available in this Krita version. Upgrade to get selection bounds info.",
            }

        try:
            bounds = selection.bounds()
            return {
                "status": "ok",
                "has_selection": True,
                "bounds": {
                    "x": bounds.x(),
                    "y": bounds.y(),
                    "width": bounds.width(),
                    "height": bounds.height(),
                },
            }
        except (AttributeError, TypeError):
            return {"status": "ok", "has_selection": True, "bounds": None}

    def cmd_get_capabilities(self, params: dict[str, Any]) -> dict[str, Any]:
        """Return detected API capabilities."""
        return self.get_capabilities()

    def cmd_get_security_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Return current security limits and usage."""
        return {
            "status": "ok",
            "rate_limit": {
                "max_commands_per_minute": rate_limiter.max_commands,
                "window_seconds": rate_limiter._window,
                "current_usage": len(rate_limiter._timestamps),
            },
            "payload_limit": MAX_PAYLOAD_SIZE,
            "batch_size_limit": MAX_BATCH_SIZE,
            "max_canvas_dim": MAX_CANVAS_DIM,
            "max_layers": MAX_LAYERS,
        }

    def cmd_transform_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Transform the current selection (move, rotate, scale)."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection to transform", code="INVALID_PARAMETERS", recoverable=True)

        try:
            dx = params.get("dx", 0)
            dy = params.get("dy", 0)
            angle = params.get("angle", 0.0)
            scale_x = params.get("scale_x", 1.0)
            scale_y = params.get("scale_y", 1.0)

            # Krita's Selection.transform takes a QTransform
            from PyQt5.QtGui import QTransform

            transform = QTransform()
            transform.translate(dx, dy)
            transform.rotate(angle)
            transform.scale(scale_x, scale_y)
            selection.transform(transform)
            doc.refreshProjection()
            return {"status": "ok", "dx": dx, "dy": dy, "angle": angle, "scale_x": scale_x, "scale_y": scale_y}
        except (AttributeError, TypeError) as exc:
            return make_error(f"Transform not supported: {exc}", code="INTERNAL_ERROR", recoverable=False)

    def cmd_grow_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Grow the current selection outward."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection to grow", code="INVALID_PARAMETERS", recoverable=True)

        pixels = params.get("pixels", 1)
        try:
            selection.grow(pixels)
            doc.refreshProjection()
            return {"status": "ok", "pixels": pixels}
        except (AttributeError, TypeError) as exc:
            return make_error(f"Grow not supported: {exc}", code="INTERNAL_ERROR", recoverable=False)

    def cmd_shrink_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Shrink the current selection inward."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection to shrink", code="INVALID_PARAMETERS", recoverable=True)

        pixels = params.get("pixels", 1)
        try:
            selection.shrink(pixels)
            doc.refreshProjection()
            return {"status": "ok", "pixels": pixels}
        except (AttributeError, TypeError) as exc:
            return make_error(f"Shrink not supported: {exc}", code="INTERNAL_ERROR", recoverable=False)

    def cmd_border_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a border around the current selection."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection for border", code="INVALID_PARAMETERS", recoverable=True)

        pixels = params.get("pixels", 1)
        try:
            selection.border(pixels)
            doc.refreshProjection()
            return {"status": "ok", "pixels": pixels}
        except (AttributeError, TypeError) as exc:
            return make_error(f"Border not supported: {exc}", code="INTERNAL_ERROR", recoverable=False)

    def cmd_combine_selections(self, params: dict[str, Any]) -> dict[str, Any]:
        """Combine the active selection with a second selection loaded from a mask file."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        operation = params.get("operation", "union")
        if operation not in ("union", "intersect", "subtract"):
            return make_error(
                "Invalid operation. Use union, intersect, or subtract", code="INVALID_PARAMETERS", recoverable=True
            )

        mask_path = str(params.get("mask_path", "")).strip()
        if not mask_path:
            return make_error("mask_path is required", code="INVALID_PARAMETERS", recoverable=True)

        current_selection = doc.selection()
        if not current_selection:
            return make_error("No active selection to combine", code="NO_SELECTION", recoverable=True)

        try:
            doc_width = doc.width()
            doc_height = doc.height()
            other_selection, _ = self._selection_from_mask_path(mask_path, doc_width, doc_height)

            from krita import Selection

            combined = Selection()
            selected_count = 0

            for y in range(doc_height):
                for x in range(doc_width):
                    current_selected = current_selection.pixelSelected(x, y)
                    other_selected = other_selection.pixelSelected(x, y)

                    if operation == "union":
                        include = current_selected or other_selected
                    elif operation == "intersect":
                        include = current_selected and other_selected
                    else:
                        include = current_selected and not other_selected

                    if include:
                        combined.select(x, y, 1, 1, 255)
                        selected_count += 1

            doc.setSelection(combined)
            doc.refreshProjection()

            return {
                "status": "ok",
                "operation": operation,
                "mask_path": mask_path,
                "selected_count": selected_count,
            }
        except FileNotFoundError:
            return make_error(f"Failed to load mask: {mask_path}", code="FILE_NOT_FOUND", recoverable=True)
        except Exception as exc:
            return make_error(f"Failed to combine selections: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_clear_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Clear the content of the selection on the active layer."""
        selection, error = self._get_selection_or_error()
        if error:
            return error
        if selection is None:
            return {"status": "ok", "message": "No active selection to clear"}

        selection.clear()
        doc = self.get_active_document()
        if doc:
            doc.refreshProjection()
        return {"status": "ok"}

    def cmd_invert_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Invert the current selection."""
        selection, error = self._get_selection_or_error()
        if error:
            return error
        if selection is None:
            return {"status": "ok", "message": "No active selection to invert"}

        selection.invert()
        doc = self.get_active_document()
        if doc:
            doc.refreshProjection()
        return {"status": "ok"}

    def cmd_fill_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fill the current selection with foreground color."""
        doc = self.get_active_document()
        view = self.get_active_view()
        if not doc or not view:
            return make_error("No active document/view", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        doc.fillSelection(view.foregroundColor())
        doc.refreshProjection()
        return {"status": "ok"}

    def cmd_deselect(self, params: dict[str, Any]) -> dict[str, Any]:
        """Remove the active selection."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        doc.setSelection(None)
        doc.refreshProjection()
        return {"status": "ok"}

    def cmd_select_by_color(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select pixels by color similarity (magic wand or global)."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        tolerance = params.get("tolerance", 0.1)
        contiguous = params.get("contiguous", True)
        x = params.get("x")
        y = params.get("y")

        try:
            # Get layer pixel data
            doc_width = doc.width()
            doc_height = doc.height()
            pixel_data = layer.pixelData(0, 0, doc_width, doc_height)

            selection = doc.selection()
            if not selection:
                # Create new selection
                from krita import Selection

                selection = Selection()

            if x is not None and y is not None and contiguous:
                # Magic wand: flood-fill from point
                target_idx = (y * doc_width + x) * 4
                target_r = pixel_data[target_idx + 2]  # BGRA format
                target_g = pixel_data[target_idx + 1]
                target_b = pixel_data[target_idx]

                # Simple flood-fill using BFS
                visited = set()
                queue = [(x, y)]
                tolerance_val = tolerance * 255

                while queue:
                    cx, cy = queue.pop(0)
                    if (cx, cy) in visited:
                        continue
                    if cx < 0 or cy < 0 or cx >= doc_width or cy >= doc_height:
                        continue

                    idx = (cy * doc_width + cx) * 4
                    r = pixel_data[idx + 2]
                    g = pixel_data[idx + 1]
                    b = pixel_data[idx]

                    # Check color distance
                    dist = ((r - target_r) ** 2 + (g - target_g) ** 2 + (b - target_b) ** 2) ** 0.5
                    if dist <= tolerance_val * 1.732:  # sqrt(3) for RGB space
                        selection.select(cx, cy, 1, 1, 255)
                        visited.add((cx, cy))
                        queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
            else:
                # Global: select all matching pixels
                tolerance_val = tolerance * 255
                if x is not None and y is not None:
                    # Use point color as reference
                    idx = (y * doc_width + x) * 4
                    target_r = pixel_data[idx + 2]
                    target_g = pixel_data[idx + 1]
                    target_b = pixel_data[idx]
                else:
                    # Use current foreground color
                    r, g, b = self._get_fg_color()
                    target_r, target_g, target_b = b, g, r  # Convert to BGRA

                for py in range(doc_height):
                    for px in range(doc_width):
                        idx = (py * doc_width + px) * 4
                        r = pixel_data[idx + 2]
                        g = pixel_data[idx + 1]
                        b = pixel_data[idx]

                        dist = ((r - target_r) ** 2 + (g - target_g) ** 2 + (b - target_b) ** 2) ** 0.5
                        if dist <= tolerance_val * 1.732:
                            selection.select(px, py, 1, 1, 255)

            doc.setSelection(selection)
            doc.refreshProjection()

            # Count selected pixels
            selected_count = len(visited) if "visited" in locals() else 0

            return {
                "status": "ok",
                "selected_count": selected_count,
                "method": "contiguous" if contiguous else "global",
                "tolerance": tolerance,
            }
        except Exception as exc:
            return make_error(f"Color selection failed: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_select_by_alpha(self, params: dict[str, Any]) -> dict[str, Any]:
        """Select pixels by alpha value range."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        min_alpha = params.get("min_alpha", 1)
        max_alpha = params.get("max_alpha", 255)

        try:
            doc_width = doc.width()
            doc_height = doc.height()
            pixel_data = layer.pixelData(0, 0, doc_width, doc_height)

            selection = doc.selection()
            if not selection:
                from krita import Selection

                selection = Selection()

            selected_count = 0
            for py in range(doc_height):
                for px in range(doc_width):
                    idx = (py * doc_width + px) * 4
                    alpha = pixel_data[idx + 3]  # Alpha channel in BGRA

                    if min_alpha <= alpha <= max_alpha:
                        selection.select(px, py, 1, 1, 255)
                        selected_count += 1

            doc.setSelection(selection)
            doc.refreshProjection()

            return {
                "status": "ok",
                "selected_count": selected_count,
                "min_alpha": min_alpha,
                "max_alpha": max_alpha,
            }
        except Exception as exc:
            return make_error(f"Alpha selection failed: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def _selection_from_mask_path(self, path: str, doc_width: int, doc_height: int) -> tuple[Any, int]:
        """Load a selection mask image into a Krita Selection object."""
        from PyQt5.QtGui import QImage
        from krita import Selection

        mask = QImage(path)
        if mask.isNull():
            raise FileNotFoundError(path)

        selection = Selection()
        loaded_pixels = 0

        for y in range(min(mask.height(), doc_height)):
            for x in range(min(mask.width(), doc_width)):
                pixel = mask.pixel(x, y)
                color = QColor(pixel)
                brightness = (color.red() + color.green() + color.blue()) // 3
                if brightness > 127:
                    selection.select(x, y, 1, 1, 255)
                    loaded_pixels += 1

        return selection, loaded_pixels

    def cmd_save_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Save current selection to a PNG mask file."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection to save", code="INVALID_PARAMETERS", recoverable=True)

        path = params.get("path", "")
        fmt = params.get("format", "png")

        try:
            from PyQt5.QtGui import QImage
            from PyQt5.QtCore import QRect

            doc_width = doc.width()
            doc_height = doc.height()
            bounds = selection.bounds()

            # Create grayscale mask image
            mask = QImage(doc_width, doc_height, QImage.Format_Grayscale8)

            # Fill mask based on selection
            for y in range(doc_height):
                for x in range(doc_width):
                    selected = selection.pixelSelected(x, y)
                    mask.setPixel(x, y, 255 if selected else 0)

            # Save to file
            if fmt.lower() == "png":
                mask.save(path, "PNG")
            else:
                mask.save(path, fmt.upper())

            # Count selected pixels
            pixel_count = 0
            for y in range(doc_height):
                for x in range(doc_width):
                    if selection.pixelSelected(x, y):
                        pixel_count += 1

            return {
                "status": "ok",
                "path": path,
                "format": fmt,
                "pixel_count": pixel_count,
            }
        except Exception as exc:
            return make_error(f"Failed to save selection: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_load_selection(self, params: dict[str, Any]) -> dict[str, Any]:
        """Load selection from a PNG mask file."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        path = params.get("path", "")

        try:
            doc_width = doc.width()
            doc_height = doc.height()
            selection, loaded_pixels = self._selection_from_mask_path(path, doc_width, doc_height)

            doc.setSelection(selection)
            doc.refreshProjection()

            return {
                "status": "ok",
                "path": path,
                "loaded_pixels": loaded_pixels,
            }
        except FileNotFoundError:
            return make_error(f"Failed to load mask: {path}", code="FILE_NOT_FOUND", recoverable=True)
        except Exception as exc:
            return make_error(f"Failed to load selection: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_selection_stats(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get statistics about the current selection."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return {"status": "ok", "has_selection": False, "pixel_count": 0}

        try:
            doc_width = doc.width()
            doc_height = doc.height()
            total_pixels = doc_width * doc_height

            pixel_count = 0
            sum_x = 0
            sum_y = 0
            bounds = selection.bounds()

            for y in range(doc_height):
                for x in range(doc_width):
                    if selection.pixelSelected(x, y):
                        pixel_count += 1
                        sum_x += x
                        sum_y += y

            centroid_x = sum_x / pixel_count if pixel_count > 0 else 0
            centroid_y = sum_y / pixel_count if pixel_count > 0 else 0
            area_percentage = (pixel_count / total_pixels * 100) if total_pixels > 0 else 0

            return {
                "status": "ok",
                "has_selection": True,
                "pixel_count": pixel_count,
                "area_percentage": round(area_percentage, 2),
                "centroid": {"x": round(centroid_x, 1), "y": round(centroid_y, 1)},
                "bounds": {
                    "x": bounds.x(),
                    "y": bounds.y(),
                    "width": bounds.width(),
                    "height": bounds.height(),
                },
            }
        except Exception as exc:
            return make_error(f"Failed to get selection stats: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_save_selection_channel(self, params: dict[str, Any]) -> dict[str, Any]:
        """Save current selection as a named channel (stored in document annotations)."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        selection = doc.selection()
        if not selection:
            return make_error("No active selection to save", code="NO_SELECTION", recoverable=True)

        name = params.get("name", "").strip()
        if not name:
            return make_error("Channel name is required", code="INVALID_PARAMS", recoverable=True)

        try:
            # Save selection as annotation on the document
            # Format: JSON string with selection bounds and pixel data
            bounds = selection.bounds()
            channel_data = {
                "type": "selection_channel",
                "name": name,
                "x": bounds.x(),
                "y": bounds.y(),
                "width": bounds.width(),
                "height": bounds.height(),
            }
            import json

            doc.setAnnotation(f"kritamcp/channel/{name}", json.dumps(channel_data))
            doc.refreshProjection()

            return {"status": "ok", "channel": name, "message": f"Saved selection channel '{name}'"}
        except Exception as exc:
            return make_error(f"Failed to save channel: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_load_selection_channel(self, params: dict[str, Any]) -> dict[str, Any]:
        """Load a named selection channel and restore it as active selection."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        name = params.get("name", "").strip()
        if not name:
            return make_error("Channel name is required", code="INVALID_PARAMS", recoverable=True)

        try:
            import json
            from krita import Selection

            data = doc.annotation(f"kritamcp/channel/{name}")
            if not data:
                return make_error(f"Channel '{name}' not found", code="CHANNEL_NOT_FOUND", recoverable=True)

            channel_info = json.loads(data)
            # Create selection from stored bounds
            selection = Selection()
            x, y = channel_info["x"], channel_info["y"]
            w, h = channel_info["width"], channel_info["height"]
            selection.select(x, y, w, h, 255)
            doc.setSelection(selection)
            doc.refreshProjection()

            return {"status": "ok", "channel": name, "message": f"Loaded selection channel '{name}'"}
        except json.JSONDecodeError:
            return make_error(f"Invalid channel data for '{name}'", code="INVALID_CHANNEL", recoverable=True)
        except Exception as exc:
            return make_error(f"Failed to load channel: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_list_selection_channels(self, params: dict[str, Any]) -> dict[str, Any]:
        """List all saved selection channels."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        try:
            import json

            channels = []
            # Iterate through document annotations to find selection channels
            annotation_keys = doc.annotations()
            for key in annotation_keys:
                if key.startswith("kritamcp/channel/"):
                    data = doc.annotation(key)
                    if data:
                        try:
                            info = json.loads(data)
                            channels.append(
                                {
                                    "name": info.get("name", key.split("/")[-1]),
                                    "bounds": {
                                        "x": info.get("x"),
                                        "y": info.get("y"),
                                        "width": info.get("width"),
                                        "height": info.get("height"),
                                    },
                                }
                            )
                        except json.JSONDecodeError:
                            channels.append({"name": key.split("/")[-1], "bounds": {}})

            return {"status": "ok", "channels": channels, "count": len(channels)}
        except Exception as exc:
            return make_error(f"Failed to list channels: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_delete_selection_channel(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a saved selection channel."""
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        name = params.get("name", "").strip()
        if not name:
            return make_error("Channel name is required", code="INVALID_PARAMS", recoverable=True)

        try:
            key = f"kritamcp/channel/{name}"
            if not doc.annotation(key):
                return make_error(f"Channel '{name}' not found", code="CHANNEL_NOT_FOUND", recoverable=True)

            doc.removeAnnotation(key)
            return {"status": "ok", "channel": name, "message": f"Deleted selection channel '{name}'"}
        except Exception as exc:
            return make_error(f"Failed to delete channel: {exc}", code="INTERNAL_ERROR", recoverable=True)

    def cmd_get_command_history(self, params: dict[str, Any]) -> dict[str, Any]:
        """Return recent command execution history."""
        limit = params.get("limit", 20)
        records = history_store.query(limit=limit)
        return {"status": "ok", "history": records, "count": len(records)}

    def cmd_open_file(self, params: dict[str, Any]) -> dict[str, Any]:
        pass

    def get_active_document(self) -> Any | None:
        app = Krita.instance()
        return app.activeDocument()

    def get_active_view(self) -> Any | None:
        app = Krita.instance()
        window = app.activeWindow()
        if window:
            return window.activeView()
        return None

    def _get_selection_or_error(self) -> tuple[Any | None, dict[str, Any] | None]:
        """Get the active selection, returning an error dict if unavailable.

        Returns:
            Tuple of (selection, error). If error is not None, selection is None.
            If selection is not None, error is None.
        """
        doc = self.get_active_document()
        if not doc:
            return None, make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)
        selection = doc.selection()
        if not selection:
            return None, None  # No selection is not an error for info/clear/invert
        return selection, None

    def _has_active_selection(self) -> bool:
        """Check if there is an active selection on the document."""
        doc = self.get_active_document()
        if not doc:
            return False
        try:
            sel = doc.selection()
            return sel is not None
        except (AttributeError, TypeError):
            return False

    def _clipping_notice(self) -> dict[str, object] | None:
        """Return a clipping notice dict if selection is active, else None."""
        if self._has_active_selection():
            return {"clipped_by_selection": True, "note": "Drawing operations are clipped to active selection"}
        return None

    def get_active_layer(self) -> Any | None:
        doc = self.get_active_document()
        if doc:
            return doc.activeNode()
        return None

    def _get_fg_color(self) -> tuple[int, int, int]:
        """Get current foreground color as (r, g, b)."""
        view = self.get_active_view()
        if not view:
            return (255, 255, 255)
        fg = view.foregroundColor()
        qcolor = fg.colorForCanvas(view.canvas())
        return (qcolor.red(), qcolor.green(), qcolor.blue())

    # -- Command implementations ---------------------------------------------

    def cmd_new_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new canvas."""
        width = params.get("width", 800)
        height = params.get("height", 600)
        name = params.get("name", "New Canvas")
        bg_color = params.get("background", "#1a1a2e")

        # Prevent OOM
        if width > MAX_CANVAS_DIM or height > MAX_CANVAS_DIM:
            return make_error(
                f"Canvas dimensions exceed maximum ({MAX_CANVAS_DIM}x{MAX_CANVAS_DIM})",
                code="CANVAS_TOO_LARGE",
                recoverable=True,
            )
        if width < 1 or height < 1:
            return make_error("Canvas dimensions must be positive", code="INVALID_PARAMETERS", recoverable=True)

        app = Krita.instance()
        doc = app.createDocument(width, height, name, "RGBA", "U8", "", 120.0)

        window = app.activeWindow()
        if window:
            window.addView(doc)

        root = doc.rootNode()
        layer = doc.createNode("paint", "paintlayer")
        root.addChildNode(layer, None)

        color = QColor(bg_color)
        r, g, b = color.red(), color.green(), color.blue()

        pixel_data = bytes([b, g, r, 255] * (width * height))
        layer.setPixelData(pixel_data, 0, 0, width, height)

        doc.refreshProjection()
        return {"status": "ok", "width": width, "height": height, "name": name}

    def cmd_set_color(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set foreground color."""
        color_hex = params.get("color", "#ffffff")
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        color = QColor(color_hex)
        mc = ManagedColor.fromQColor(color, view.canvas())
        view.setForeGroundColor(mc)
        return {"status": "ok", "color": color_hex}

    def cmd_set_brush(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set brush preset and size."""
        preset_name = params.get("preset")
        size = params.get("size")
        opacity = params.get("opacity")

        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        if preset_name:
            presets = Krita.instance().resources("preset")
            found = None
            for pname, preset in presets.items():
                if preset_name.lower() in pname.lower():
                    found = preset
                    break
            if found:
                view.setCurrentBrushPreset(found)
            else:
                return make_error(f"Brush preset not found: {preset_name}", code="BRUSH_NOT_FOUND", recoverable=True)

        if size is not None:
            self.current_brush_size = size
            view.setBrushSize(size)

        if opacity is not None:
            self.current_opacity = opacity

        return {"status": "ok"}

    def cmd_stroke(self, params: dict[str, Any]) -> dict[str, Any]:
        """Paint a stroke along points using pixel-level drawing with soft edges."""
        points = params.get("points", [])
        brush_size = params.get("size", self.current_brush_size)
        hardness = params.get("hardness", 0.5)
        opacity = params.get("opacity", 1.0)
        pressure = params.get("pressure", 1.0)

        # Map pressure to hardness if hardness not explicitly set
        if "hardness" not in params and "pressure" in params:
            hardness = pressure

        if len(points) < 2:
            return make_error("Need at least 2 points for a stroke", code="INVALID_PARAMETERS", recoverable=True)

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        r, g, b = self._get_fg_color()
        doc_width = doc.width()
        doc_height = doc.height()
        radius = max(1, brush_size // 2)

        min_x = max(0, int(min(p[0] for p in points)) - radius - 2)
        min_y = max(0, int(min(p[1] for p in points)) - radius - 2)
        max_x = min(doc_width, int(max(p[0] for p in points)) + radius + 2)
        max_y = min(doc_height, int(max(p[1] for p in points)) + radius + 2)

        w = max_x - min_x
        h = max_y - min_y

        if w <= 0 or h <= 0:
            return make_error("Stroke out of bounds", code="INVALID_PARAMETERS", recoverable=True)

        existing = layer.pixelData(min_x, min_y, w, h)

        if HAS_NUMPY:
            pixels = self._draw_stroke_numpy(bytearray(existing), w, h, points, radius, hardness, opacity, r, g, b)
        else:
            pixels = self._draw_stroke_python(bytearray(existing), w, h, points, radius, hardness, opacity, r, g, b)

        layer.setPixelData(bytes(pixels), min_x, min_y, w, h)
        doc.refreshProjection()
        result: dict[str, object] = {"status": "ok", "points_count": len(points), "hardness": hardness}
        clipping = self._clipping_notice()
        if clipping:
            result.update(clipping)  # type: ignore[arg-type]
        return result

    @staticmethod
    def _draw_stroke_python(
        pixels: bytearray,
        w: int,
        h: int,
        points: list[list[int]],
        radius: int,
        hardness: float,
        opacity: float,
        r: int,
        g: int,
        b: int,
    ) -> bytearray:
        """Draw stroke using pure Python (fallback when numpy unavailable)."""
        min_x = 0
        min_y = 0

        def draw_soft_circle(cx: int, cy: int) -> None:
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= radius * radius:
                        px = cx + dx - min_x
                        py = cy + dy - min_y
                        if 0 <= px < w and 0 <= py < h:
                            dist = math.sqrt(dist_sq) / radius if radius > 0 else 0
                            if hardness >= 1.0 or dist < hardness:
                                alpha_factor = 1.0
                            else:
                                falloff = (dist - hardness) / (1.0 - hardness)
                                alpha_factor = 1.0 - falloff

                            final_alpha = int(255 * alpha_factor * opacity)
                            if final_alpha > 0:
                                idx = (py * w + px) * 4
                                blend = final_alpha / 255.0
                                pixels[idx] = int(pixels[idx] * (1 - blend) + b * blend)
                                pixels[idx + 1] = int(pixels[idx + 1] * (1 - blend) + g * blend)
                                pixels[idx + 2] = int(pixels[idx + 2] * (1 - blend) + r * blend)
                                pixels[idx + 3] = max(pixels[idx + 3], final_alpha)

        def draw_line(x1: int, y1: int, x2: int, y2: int) -> None:
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            steps = max(1, int(dist / max(1, radius / 3)))
            for i in range(steps + 1):
                t = i / steps if steps > 0 else 0
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                draw_soft_circle(int(x), int(y))

        for i in range(len(points)):
            draw_soft_circle(points[i][0], points[i][1])
            if i > 0:
                draw_line(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1])

        return pixels

    @staticmethod
    def _draw_stroke_numpy(
        pixels: bytearray,
        w: int,
        h: int,
        points: list[list[int]],
        radius: int,
        hardness: float,
        opacity: float,
        r: int,
        g: int,
        b: int,
    ) -> bytearray:
        """Draw stroke using numpy vectorization (100-1000x faster)."""
        img = np.frombuffer(pixels, dtype=np.uint8).reshape((h, w, 4)).copy()
        ys, xs = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        dist_sq = xs * xs + ys * ys
        mask = dist_sq <= radius * radius
        dist = np.sqrt(dist_sq) / radius
        if hardness >= 1.0:
            alpha_factor = np.ones_like(dist)
        else:
            alpha_factor = np.where(
                dist < hardness,
                1.0,
                1.0 - (dist - hardness) / (1.0 - hardness),
            )
        alpha_factor = np.clip(alpha_factor, 0.0, 1.0)
        final_alpha = (255 * alpha_factor * opacity).astype(np.uint8)

        def apply_circle(cx: int, cy: int) -> None:
            x0 = max(0, cx - radius)
            y0 = max(0, cy - radius)
            x1 = min(w, cx + radius + 1)
            y1 = min(h, cy + radius + 1)
            if x0 >= x1 or y0 >= y1:
                return
            sx = radius - (cx - x0)
            sy = radius - (cy - y0)
            a = final_alpha[sy : y1 - y0 + sy, sx : x1 - x0 + sx]
            blend = a.astype(np.float32) / 255.0
            region = img[y0:y1, x0:x1].astype(np.float32)
            region[..., 0] = region[..., 0] * (1 - blend) + b * blend
            region[..., 1] = region[..., 1] * (1 - blend) + g * blend
            region[..., 2] = region[..., 2] * (1 - blend) + r * blend
            region[..., 3] = np.maximum(region[..., 3], a.astype(np.float32))
            img[y0:y1, x0:x1] = region.astype(np.uint8)

        for i in range(len(points)):
            apply_circle(points[i][0], points[i][1])
            if i > 0:
                x1, y1 = points[i - 1]
                x2, y2 = points[i]
                dist = max(abs(x2 - x1), abs(y2 - y1))
                steps = max(1, int(dist))
                for j in range(steps + 1):
                    t = j / steps if steps > 0 else 0
                    apply_circle(int(x1 + t * (x2 - x1)), int(y1 + t * (y2 - y1)))

        return bytearray(img.tobytes())

    def cmd_fill(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fill a circular area with current color."""
        x = params.get("x", 0)
        y = params.get("y", 0)
        radius = params.get("radius", 50)

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        r, g, b = self._get_fg_color()
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(doc.width(), x + radius)
        y2 = min(doc.height(), y + radius)
        w = x2 - x1
        h = y2 - y1

        if w <= 0 or h <= 0:
            return make_error("Fill area out of bounds", code="INVALID_PARAMETERS", recoverable=True)

        existing = layer.pixelData(x1, y1, w, h)
        pixels = bytearray(existing)

        for py in range(h):
            for px in range(w):
                dx = (x1 + px) - x
                dy = (y1 + py) - y
                if dx * dx + dy * dy <= radius * radius:
                    idx = (py * w + px) * 4
                    pixels[idx] = b
                    pixels[idx + 1] = g
                    pixels[idx + 2] = r
                    pixels[idx + 3] = 255

        layer.setPixelData(bytes(pixels), x1, y1, w, h)
        doc.refreshProjection()
        result: dict[str, object] = {"status": "ok", "x": x, "y": y, "radius": radius}
        clipping = self._clipping_notice()
        if clipping:
            result.update(clipping)  # type: ignore[arg-type]
        return result

    def cmd_draw_shape(self, params: dict[str, Any]) -> dict[str, Any]:
        """Draw a shape (rectangle, ellipse, line)."""
        shape = params.get("shape", "rectangle")
        x = params.get("x", 0)
        y = params.get("y", 0)
        width = params.get("width", 100)
        height = params.get("height", 100)
        fill = params.get("fill", True)
        stroke = params.get("stroke", False)

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view", code="NO_ACTIVE_VIEW", recoverable=True)

        r, g, b = self._get_fg_color()
        doc_width = doc.width()
        doc_height = doc.height()

        if shape == "line":
            x2 = params.get("x2", x + width)
            y2 = params.get("y2", y + height)
            line_width = params.get("line_width", 2)

            x1_bound = max(0, int(min(x, x2)) - line_width)
            y1_bound = max(0, int(min(y, y2)) - line_width)
            x2_bound = min(doc_width, int(max(x, x2)) + line_width)
            y2_bound = min(doc_height, int(max(y, y2)) + line_width)
            w = x2_bound - x1_bound
            h = y2_bound - y1_bound

            if w > 0 and h > 0:
                existing = layer.pixelData(x1_bound, y1_bound, w, h)
                pixels = bytearray(existing)
                radius = max(1, line_width // 2)
                dist = max(abs(x2 - x), abs(y2 - y))
                steps = max(1, int(dist))

                for i in range(steps + 1):
                    t = i / steps if steps > 0 else 0
                    cx = x + t * (x2 - x)
                    cy = y + t * (y2 - y)
                    for dy in range(-radius, radius + 1):
                        for dx in range(-radius, radius + 1):
                            if dx * dx + dy * dy <= radius * radius:
                                px = int(cx) + dx - x1_bound
                                py = int(cy) + dy - y1_bound
                                if 0 <= px < w and 0 <= py < h:
                                    idx = (py * w + px) * 4
                                    pixels[idx] = b
                                    pixels[idx + 1] = g
                                    pixels[idx + 2] = r
                                    pixels[idx + 3] = 255

                layer.setPixelData(bytes(pixels), x1_bound, y1_bound, w, h)

        elif shape == "rectangle":
            sx1 = max(0, int(x))
            sy1 = max(0, int(y))
            sx2 = min(doc_width, int(x + width))
            sy2 = min(doc_height, int(y + height))
            sw = sx2 - sx1
            sh = sy2 - sy1

            if sw > 0 and sh > 0:
                if fill:
                    pixel_data = bytes([b, g, r, 255] * (sw * sh))
                    layer.setPixelData(pixel_data, sx1, sy1, sw, sh)
                if stroke:
                    existing = layer.pixelData(sx1, sy1, sw, sh)
                    pixels = bytearray(existing)
                    for px in range(sw):
                        for py in range(sh):
                            if px == 0 or px == sw - 1 or py == 0 or py == sh - 1:
                                idx = (py * sw + px) * 4
                                pixels[idx] = b
                                pixels[idx + 1] = g
                                pixels[idx + 2] = r
                                pixels[idx + 3] = 255
                    layer.setPixelData(bytes(pixels), sx1, sy1, sw, sh)

        elif shape == "ellipse":
            cx = x + width / 2
            cy = y + height / 2
            rx = width / 2
            ry = height / 2

            sx1 = max(0, int(x))
            sy1 = max(0, int(y))
            sx2 = min(doc_width, int(x + width))
            sy2 = min(doc_height, int(y + height))
            sw = sx2 - sx1
            sh = sy2 - sy1

            if sw > 0 and sh > 0:
                existing = layer.pixelData(sx1, sy1, sw, sh)
                pixels = bytearray(existing)

                for py in range(sh):
                    for px in range(sw):
                        dx = (sx1 + px - cx) / rx if rx > 0 else 0
                        dy = (sy1 + py - cy) / ry if ry > 0 else 0
                        val = dx * dx + dy * dy
                        if (fill and val <= 1) or (stroke and 0.9 <= val <= 1.1):
                            idx = (py * sw + px) * 4
                            pixels[idx] = b
                            pixels[idx + 1] = g
                            pixels[idx + 2] = r
                            pixels[idx + 3] = 255

                layer.setPixelData(bytes(pixels), sx1, sy1, sw, sh)
        else:
            return make_error(f"Shape '{shape}' not supported", code="INVALID_SHAPE", recoverable=True)

        doc.refreshProjection()
        result: dict[str, object] = {"status": "ok", "shape": shape}
        clipping = self._clipping_notice()
        if clipping:
            result.update(clipping)  # type: ignore[arg-type]
        return result

    def cmd_get_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        """Export current canvas to file and return path."""
        filename = params.get("filename", "canvas.png")
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        if not filename.endswith(".png"):
            filename += ".png"

        filepath = os.path.join(CANVAS_OUTPUT_DIR, filename)
        doc.setBatchmode(True)
        doc.exportImage(filepath, InfoObject())
        doc.setBatchmode(False)
        return {"status": "ok", "path": filepath}

    def cmd_undo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Undo last action."""
        app = Krita.instance()
        action = app.action("edit_undo")
        if action:
            action.trigger()
            return {"status": "ok"}
        return make_error("Could not trigger undo", code="INTERNAL_ERROR", recoverable=True)

    def cmd_redo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Redo last undone action."""
        app = Krita.instance()
        action = app.action("edit_redo")
        if action:
            action.trigger()
            return {"status": "ok"}
        return make_error("Could not trigger redo", code="INTERNAL_ERROR", recoverable=True)

    def cmd_clear(self, params: dict[str, Any]) -> dict[str, Any]:
        """Clear the canvas."""
        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer", code="NO_ACTIVE_LAYER", recoverable=True)

        doc = self.get_active_document()
        width = doc.width()
        height = doc.height()

        # Prevent OOM on very large canvases
        if width * height > MAX_CANVAS_DIM * MAX_CANVAS_DIM:
            return make_error(
                f"Canvas too large to clear (max {MAX_CANVAS_DIM}x{MAX_CANVAS_DIM})",
                code="CANVAS_TOO_LARGE",
                recoverable=True,
            )

        bg_color = params.get("color", "#1a1a2e")
        color = QColor(bg_color)
        r, g, b = color.red(), color.green(), color.blue()

        pixel_data = bytes([b, g, r, 255] * (width * height))
        layer.setPixelData(pixel_data, 0, 0, width, height)
        doc.refreshProjection()
        return {"status": "ok", "color": bg_color}

    def cmd_save(self, params: dict[str, Any]) -> dict[str, Any]:
        """Save to specific path."""
        filepath = params.get("path")
        if not filepath:
            return make_error("No path specified", code="INVALID_PARAMETERS", recoverable=True)

        # Path traversal prevention
        if ".." in filepath:
            return make_error("Path traversal is not allowed", code="PATH_TRAVERSAL_BLOCKED", recoverable=False)

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        doc.setBatchmode(True)
        doc.exportImage(filepath, InfoObject())
        doc.setBatchmode(False)
        return {"status": "ok", "path": filepath}

    def cmd_get_color_at(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get color at specific pixel (eyedropper)."""
        x = params.get("x", 0)
        y = params.get("y", 0)

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        layer = doc.rootNode()
        pixel_data = layer.projectionPixelData(x, y, 1, 1)

        if len(pixel_data) >= 4:
            b_val, g_val, r_val, a_val = pixel_data[0], pixel_data[1], pixel_data[2], pixel_data[3]
            hex_color = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
            return {
                "status": "ok",
                "color": hex_color,
                "r": r_val,
                "g": g_val,
                "b": b_val,
                "a": a_val,
            }

        return make_error("Could not read pixel", code="INTERNAL_ERROR", recoverable=True)

    def cmd_list_brushes(self, params: dict[str, Any]) -> dict[str, Any]:
        """List available brush presets."""
        filter_str = params.get("filter", "")
        limit = params.get("limit", 50)

        presets = Krita.instance().resources("preset")
        brush_list: list[str] = []

        for name in presets:
            if filter_str.lower() in name.lower():
                brush_list.append(name)
                if len(brush_list) >= limit:
                    break

        return {"status": "ok", "brushes": brush_list, "count": len(brush_list)}

    def cmd_open_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """Open an existing file in Krita."""
        filepath = params.get("path")
        if not filepath:
            return make_error("No path specified", code="INVALID_PARAMETERS", recoverable=True)

        # Path traversal prevention
        if ".." in filepath:
            return make_error("Path traversal is not allowed", code="PATH_TRAVERSAL_BLOCKED", recoverable=False)

        if not os.path.exists(filepath):
            return make_error(f"File not found: {filepath}", code="FILE_NOT_FOUND", recoverable=True)

        app = Krita.instance()
        doc = app.openDocument(filepath)
        if not doc:
            return make_error(f"Failed to open: {filepath}", code="INTERNAL_ERROR", recoverable=True)

        window = app.activeWindow()
        if window:
            window.addView(doc)

        return {
            "status": "ok",
            "path": filepath,
            "name": doc.name(),
            "width": doc.width(),
            "height": doc.height(),
        }

    def cmd_batch(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute multiple commands sequentially."""
        commands = params.get("commands", [])
        stop_on_error = params.get("stop_on_error", False)
        results: list[dict[str, Any]] = []

        # Take snapshot before batch for potential rollback
        doc = self.get_active_document()
        batch_id = None
        if doc:
            snapshot_path = os.path.join(self.snapshot_store.snapshot_dir, f"before_{uuid.uuid4()}.png")
            doc.setBatchmode(True)
            doc.exportImage(snapshot_path, InfoObject())
            doc.setBatchmode(False)
            batch_id = self.snapshot_store.create_snapshot(commands, snapshot_path)

        ok_count = 0
        err_count = 0

        for cmd in commands:
            action = cmd.get("action")
            cmd_params = cmd.get("params", {})
            try:
                result = self.execute_command({"action": action, "params": cmd_params})
                if "error" in result:
                    results.append({"action": action, "status": "error", "result": result})
                    err_count += 1
                    if stop_on_error:
                        break
                else:
                    results.append({"action": action, "status": "ok", "result": result})
                    ok_count += 1
            except Exception as exc:
                results.append({"action": action, "status": "error", "error": str(exc)})
                err_count += 1
                if stop_on_error:
                    break

        status = "ok"
        if ok_count > 0 and err_count > 0:
            status = "partial"
        elif err_count > 0:
            status = "error"

        response = {
            "status": status,
            "results": results,
            "count": len(results),
        }
        if batch_id:
            response["batch_id"] = batch_id

        return response

    def cmd_rollback(self, params: dict[str, Any]) -> dict[str, Any]:
        """Roll back a batch execution using a snapshot."""
        batch_id = params.get("batch_id")
        if not batch_id:
            return make_error("Missing batch_id", code="INVALID_PARAMETERS", recoverable=True)

        snapshot = self.snapshot_store.get_snapshot(batch_id)
        if not snapshot:
            return make_error(f"Batch snapshot not found: {batch_id}", code="BATCH_NOT_FOUND", recoverable=True)

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document", code="NO_ACTIVE_DOCUMENT", recoverable=True)

        from PyQt5.QtGui import QImage

        qimg = QImage(snapshot.canvas_before_path)
        if qimg.isNull():
            return make_error("Failed to load snapshot image", code="INTERNAL_ERROR", recoverable=False)

        # SECURITY/VALIDATION: Check if canvas state has changed (dimensions check as proxy)
        if qimg.width() != doc.width() or qimg.height() != doc.height():
            return make_error(
                "Canvas dimensions have changed since batch execution. Rollback not possible.",
                code="ROLLBACK_NOT_POSSIBLE",
                recoverable=False,
            )

        # Restore state: Create a new layer with the snapshot image
        # This is a safe way to 'rollback' the visual state.
        layer_name = f"Rollback_{batch_id[:8]}"
        new_layer = doc.createNode(layer_name, "paintlayer")
        doc.rootNode().addChildNode(new_layer, None)

        # Convert QImage to pixel data (BGRA)
        # Krita uses BGRA8
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        pixel_data = bytes(ptr)

        new_layer.setPixelData(pixel_data, 0, 0, qimg.width(), qimg.height())
        doc.setActiveNode(new_layer)
        doc.refreshProjection()

        # Remove the snapshot from store after successful rollback
        self.snapshot_store.remove_snapshot(batch_id)

        return {
            "status": "ok",
            "message": (
                f"Rolled back batch {batch_id}. A new layer '{layer_name}' shows "
                f"the pre-batch canvas state. Original batch layers remain underneath."
            ),
        }


# Register the extension
if "pytest" not in sys.modules:
    try:
        Krita.instance().addExtension(KritaMCPExtension(Krita.instance()))
        _log_diag("Krita.instance().addExtension completed")
    except (NameError, AttributeError) as exc:
        # Krita not defined or instance() not available
        _log_diag(f"Extension registration unavailable: {exc}")
        pass
    except Exception as exc:
        _log_diag(f"Extension registration failed: {exc}")
        pass
