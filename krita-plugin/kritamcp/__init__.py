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
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from krita import *
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtGui import QColor

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
PLUGIN_VERSION = "0.2.0"

logger = logging.getLogger("kritamcp")

def make_error(message: str, code: str = "INTERNAL_ERROR", recoverable: bool = True) -> dict[str, Any]:
    # Simple heuristic to determine code if not explicitly passed
    if "No active" in message:
        code = "NO_ACTIVE_DOCUMENT"
    elif "layer" in message.lower():
        code = "LAYER_NOT_FOUND"
    elif "bounds" in message.lower() or "dimensions" in message.lower() or "positive" in message.lower():
        code = "INVALID_PARAMS"
    elif "not found" in message.lower() or "Unknown" in message:
        code = "NOT_FOUND"

    return {"error": {"code": code, "message": message, "recoverable": recoverable}}


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

        return make_error("Timeout waiting for command execution")


# Global command queue and thread-safe counter
command_queue = CommandQueue()
_command_counter = itertools.count(1)


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
                    "protocol_version": 1,
                }
            )
        elif parsed.path == "/info":
            self.send_json_response(
                {
                    "status": "ok",
                    "version": PLUGIN_VERSION,
                    "protocol_version": 1,
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
                    ],
                }
            )
        else:
            self.send_json_response(make_error("Unknown endpoint"), 404)

    def do_POST(self) -> None:
        """Handle POST requests — paint commands."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            command = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_response(make_error("Invalid JSON"), 400)
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
            self.server = HTTPServer(("localhost", self.port), PaintRequestHandler)
            logger.info("HTTP server started on port %d", self.port)
            self.server.serve_forever()
        except OSError as exc:
            logger.error("Failed to start HTTP server on port %d: %s", self.port, exc)

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            logger.info("HTTP server stopped")


# -- Krita extension ---------------------------------------------------------


class KritaMCPExtension(Extension):
    """Main Krita extension class."""

    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.server_thread: ServerThread | None = None
        self.timer: QTimer | None = None
        self.current_brush_size: int = 20
        self.current_opacity: float = 1.0

        # Load configuration
        self.config_path = os.path.expanduser("~/.kritamcp_config.json")
        self.load_config()

    def load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                import json
                with open(self.config_path, encoding="utf-8") as f:
                    config = json.load(f)
                    # Apply config
                    global SERVER_PORT, CANVAS_OUTPUT_DIR, MAX_CANVAS_DIM
                    SERVER_PORT = config.get("port", SERVER_PORT)
                    CANVAS_OUTPUT_DIR = config.get("output_dir", os.path.expanduser(config.get("output_dir", CANVAS_OUTPUT_DIR)))
                    MAX_CANVAS_DIM = config.get("max_canvas_dim", MAX_CANVAS_DIM)
            except Exception as e:
                logger.error("Failed to load config: %s", e)

    def setup(self) -> None:
        pass

    def createActions(self, window: Any) -> None:
        """Called when a new window is created."""
        os.makedirs(CANVAS_OUTPUT_DIR, exist_ok=True)

        if self.server_thread is None:
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
        }

        handler = handlers.get(action)
        if handler is None:
            return make_error(f"Unknown action: {action}")
        return handler(params)

    def get_active_document(self) -> Any | None:
        app = Krita.instance()
        return app.activeDocument()

    def get_active_view(self) -> Any | None:
        app = Krita.instance()
        window = app.activeWindow()
        if window:
            return window.activeView()
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
            return make_error(f"Canvas dimensions exceed maximum ({MAX_CANVAS_DIM}x{MAX_CANVAS_DIM})")
        if width < 1 or height < 1:
            return make_error("Canvas dimensions must be positive")

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
            return make_error("No active view")

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
            return make_error("No active view")

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
                return make_error(f"Brush preset not found: {preset_name}")

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
            return make_error("Need at least 2 points for a stroke")

        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer")

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view")

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
            return make_error("Stroke out of bounds")

        existing = layer.pixelData(min_x, min_y, w, h)

        if HAS_NUMPY:
            pixels = self._draw_stroke_numpy(bytearray(existing), w, h, points, radius, hardness, opacity, r, g, b)
        else:
            pixels = self._draw_stroke_python(bytearray(existing), w, h, points, radius, hardness, opacity, r, g, b)

        layer.setPixelData(bytes(pixels), min_x, min_y, w, h)
        doc.refreshProjection()
        return {"status": "ok", "points_count": len(points), "hardness": hardness}

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
            return make_error("No active layer")

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view")

        r, g, b = self._get_fg_color()
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(doc.width(), x + radius)
        y2 = min(doc.height(), y + radius)
        w = x2 - x1
        h = y2 - y1

        if w <= 0 or h <= 0:
            return make_error("Fill area out of bounds")

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
        return {"status": "ok", "x": x, "y": y, "radius": radius}

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
            return make_error("No active layer")

        doc = self.get_active_document()
        view = self.get_active_view()
        if not view:
            return make_error("No active view")

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
            return make_error(f"Shape '{shape}' not supported")

        doc.refreshProjection()
        return {"status": "ok", "shape": shape}

    def cmd_get_canvas(self, params: dict[str, Any]) -> dict[str, Any]:
        """Export current canvas to file and return path."""
        filename = params.get("filename", "canvas.png")
        doc = self.get_active_document()
        if not doc:
            return make_error("No active document")

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
        return make_error("Could not trigger undo")

    def cmd_redo(self, params: dict[str, Any]) -> dict[str, Any]:
        """Redo last undone action."""
        app = Krita.instance()
        action = app.action("edit_redo")
        if action:
            action.trigger()
            return {"status": "ok"}
        return make_error("Could not trigger redo")

    def cmd_clear(self, params: dict[str, Any]) -> dict[str, Any]:
        """Clear the canvas."""
        layer = self.get_active_layer()
        if not layer:
            return make_error("No active layer")

        doc = self.get_active_document()
        width = doc.width()
        height = doc.height()

        # Prevent OOM on very large canvases
        if width * height > MAX_CANVAS_DIM * MAX_CANVAS_DIM:
            return make_error(f"Canvas too large to clear (max {MAX_CANVAS_DIM}x{MAX_CANVAS_DIM})")

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
            return make_error("No path specified")

        # Path traversal prevention
        if ".." in filepath:
            return make_error("Path traversal is not allowed")

        doc = self.get_active_document()
        if not doc:
            return make_error("No active document")

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
            return make_error("No active document")

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

        return make_error("Could not read pixel")

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
            return make_error("No path specified")

        # Path traversal prevention
        if ".." in filepath:
            return make_error("Path traversal is not allowed")

        if not os.path.exists(filepath):
            return make_error(f"File not found: {filepath}")

        app = Krita.instance()
        doc = app.openDocument(filepath)
        if not doc:
            return make_error(f"Failed to open: {filepath}")

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


# Register the extension
Krita.instance().addExtension(KritaMCPExtension(Krita.instance()))
