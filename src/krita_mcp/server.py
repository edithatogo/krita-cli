"""Krita MCP Server — FastMCP interface for AI agents.

Exposes painting tools to any MCP client (Claude, etc.) by wrapping
the krita_client library.
"""

from __future__ import annotations

from fastmcp import FastMCP

from krita_client import (
    ClientConfig,
    KritaClient,
    KritaConnectionError,
    KritaError,
)

# Configuration
_client: KritaClient | None = None


def _get_client() -> KritaClient:
    """Get or create the Krita client singleton."""
    global _client
    if _client is None:
        config = ClientConfig()
        _client = KritaClient(config)
    return _client


def _format_error(exc: KritaError) -> str:
    """Format a Krita error for MCP response."""
    if exc.code:
        return f"[{exc.code}] {exc.message}"
    return exc.message


mcp = FastMCP("krita-mcp")


@mcp.tool()
def krita_health() -> str:
    """Check if Krita is running and the MCP plugin is active."""
    try:
        client = _get_client()
        result = client.health()
        plugin = result.get("plugin", "unknown")
        status = result.get("status", "unknown")
        return f"Krita is running. Plugin: {plugin} ({status})"
    except KritaConnectionError as exc:
        return f"Cannot connect to Krita. Make sure Krita is running with the MCP plugin enabled. ({exc.message})"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_new_canvas(
    width: int = 800,
    height: int = 600,
    name: str = "New Canvas",
    background: str = "#1a1a2e",
) -> str:
    """Create a new canvas in Krita.

    Args:
        width: Canvas width in pixels (default 800, max 8192)
        height: Canvas height in pixels (default 600, max 8192)
        name: Document name
        background: Background color as hex (default dark blue)
    """
    try:
        client = _get_client()
        result = client.new_canvas(
            width=width,
            height=height,
            name=name,
            background=background,
        )
        if "error" in result:
            return f"Error: {result['error']}"
        w = result.get("width", width)
        h = result.get("height", height)
        return f"Created canvas: {w}x{h}, background: {background}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_set_color(color: str) -> str:
    """Set the foreground paint color.

    Args:
        color: Hex color code (e.g., "#ff6b6b", "#b8a9c9")
    """
    try:
        client = _get_client()
        result = client.set_color(color=color)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Color set to {color}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_set_brush(
    preset: str | None = None,
    size: int | None = None,
    opacity: float | None = None,
) -> str:
    """Set brush preset and properties.

    Args:
        preset: Brush preset name (partial match, e.g., "Basic", "Soft", "Airbrush")
        size: Brush size in pixels
        opacity: Brush opacity (0.0 to 1.0)
    """
    try:
        client = _get_client()
        result = client.set_brush(preset=preset, size=size, opacity=opacity)
        if "error" in result:
            return f"Error: {result['error']}"
        parts = []
        if preset:
            parts.append(f"preset={preset}")
        if size is not None:
            parts.append(f"size={size}")
        if opacity is not None:
            parts.append(f"opacity={opacity}")
        return f"Brush set: {', '.join(parts) if parts else 'no changes'}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_stroke(
    points: list[list[int]],
    pressure: float = 1.0,
    size: int | None = None,
    hardness: float = 0.5,
    opacity: float = 1.0,
) -> str:
    """Paint a stroke through a series of points.

    Args:
        points: List of [x, y] coordinate pairs, e.g., [[100, 100], [150, 120], [200, 150]]
        pressure: Brush pressure (0.0 to 1.0, affects stroke thickness/opacity)
        size: Brush size in pixels (overrides current brush size)
        hardness: Stroke hardness (0.0 = very soft, 1.0 = hard edge)
        opacity: Stroke opacity (0.0 to 1.0)
    """
    try:
        client = _get_client()
        result = client.stroke(
            points=points,
            pressure=pressure,
            size=size,
            hardness=hardness,
            opacity=opacity,
        )
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Stroke painted with {len(points)} points"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_fill(x: int, y: int, radius: int = 50) -> str:
    """Fill an area with current color (paints a filled circle at the point).

    Args:
        x: X coordinate
        y: Y coordinate
        radius: Fill radius in pixels
    """
    try:
        client = _get_client()
        result = client.fill(x=x, y=y, radius=radius)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Filled at ({x}, {y}) with radius {radius}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_draw_shape(
    shape: str,
    x: int,
    y: int,
    width: int = 100,
    height: int = 100,
    fill: bool = True,
    stroke: bool = False,
    x2: int | None = None,
    y2: int | None = None,
) -> str:
    """Draw a shape on the canvas.

    Args:
        shape: Type of shape - "rectangle", "ellipse", or "line"
        x: X coordinate (top-left for shapes, start point for lines)
        y: Y coordinate (top-left for shapes, start point for lines)
        width: Width of shape (ignored for lines if x2/y2 provided)
        height: Height of shape (ignored for lines if x2/y2 provided)
        fill: Whether to fill the shape
        stroke: Whether to draw outline
        x2: End X for lines (optional)
        y2: End Y for lines (optional)
    """
    try:
        client = _get_client()
        result = client.draw_shape(
            shape=shape,
            x=x,
            y=y,
            width=width,
            height=height,
            fill=fill,
            stroke=stroke,
            x2=x2,
            y2=y2,
        )
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Drew {shape} at ({x}, {y})"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_canvas(filename: str = "canvas.png") -> str:
    """Export current canvas to a PNG file and return the path.
    Use this to see your painting progress.

    Args:
        filename: Output filename (saved to configured output directory)
    """
    try:
        client = _get_client()
        result = client.get_canvas(filename=filename)
        if "error" in result:
            return f"Error: {result['error']}"
        path = result.get("path", "")
        return f"Canvas saved to: {path}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_undo() -> str:
    """Undo the last action."""
    try:
        client = _get_client()
        result = client.undo()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Undone"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_redo() -> str:
    """Redo the last undone action."""
    try:
        client = _get_client()
        result = client.redo()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Redone"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_clear(color: str = "#1a1a2e") -> str:
    """Clear the canvas to a solid color.

    Args:
        color: Color to fill canvas with (default dark blue)
    """
    try:
        client = _get_client()
        result = client.clear(color=color)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Canvas cleared to {color}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_save(path: str) -> str:
    """Save the current canvas to a specific file path.

    Args:
        path: Full file path to save to (e.g., "C:/art/my_painting.png")
    """
    try:
        client = _get_client()
        result = client.save(path=path)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Saved to {path}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_color_at(x: int, y: int) -> str:
    """Sample the color at a specific pixel (eyedropper).

    Args:
        x: X coordinate
        y: Y coordinate
    """
    try:
        client = _get_client()
        result = client.get_color_at(x=x, y=y)
        if "error" in result:
            return f"Error: {result['error']}"
        color = result.get("color", "unknown")
        r = result.get("r")
        g = result.get("g")
        b = result.get("b")
        return f"Color at ({x}, {y}): {color} (R:{r}, G:{g}, B:{b})"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_list_brushes(filter: str = "", limit: int = 20) -> str:
    """List available brush presets.

    Args:
        filter: Filter brushes by name (partial match)
        limit: Maximum number to return
    """
    try:
        client = _get_client()
        result = client.list_brushes(filter=filter, limit=limit)
        if "error" in result:
            return f"Error: {result['error']}"
        brushes_raw = result.get("brushes", [])
        brushes = list(brushes_raw) if isinstance(brushes_raw, list) else []
        if not brushes:
            return "No brushes found matching filter"
        return f"Available brushes ({len(brushes)}):\n" + "\n".join(f"  - {b}" for b in brushes)
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_open_file(path: str) -> str:
    """Open an existing file in Krita (.kra, .png, .jpg, etc).

    Args:
        path: Full file path to open (e.g., "C:/art/my_painting.kra")
    """
    try:
        client = _get_client()
        result = client.open_file(path=path)
        if "error" in result:
            return f"Error: {result['error']}"
        name = result.get("name", "unknown")
        w = result.get("width")
        h = result.get("height")
        return f"Opened: {name} ({w}x{h})"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_batch(
    commands: list[dict],
    stop_on_error: bool = False,
) -> str:
    """Execute multiple commands in a single batch.

    Args:
        commands: List of command objects, each with "action" and optional "params"
        stop_on_error: Stop executing remaining commands on first error
    """
    try:
        client = _get_client()
        result = client.batch_execute(commands, stop_on_error=stop_on_error)
        results = result.get("results", [])
        ok = sum(1 for r in results if r.get("status") == "ok")
        errs = sum(1 for r in results if r.get("status") == "error")
        summary = f"Batch: {ok} succeeded, {errs} failed out of {len(results)}"

        batch_id = result.get("batch_id")
        if batch_id:
            summary += f" (Batch ID: {batch_id})"

        if errs > 0:
            error_details = []
            for r in results:
                if r.get("status") == "error":
                    # Try to get error from top level first, then from nested result
                    err_msg = r.get("error")
                    if not err_msg:
                        result_data = r.get("result", {})
                        if isinstance(result_data, dict) and "error" in result_data:
                            err_info = result_data["error"]
                            if isinstance(err_info, dict):
                                err_msg = err_info.get("message", str(err_info))
                            else:
                                err_msg = str(err_info)

                    if not err_msg:
                        err_msg = "unknown"

                    error_details.append(f"  - {r.get('action')}: {err_msg}")
            summary += "\nErrors:\n" + "\n".join(error_details)
        return summary
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_rollback(
    batch_id: str,
) -> str:
    """Roll back a previously executed batch operation.

    This restores the canvas state to what it was before the batch started.
    Note: Snapshots are lost if the Krita plugin is restarted.

    Args:
        batch_id: The unique ID returned by a previous krita_batch call.
    """
    try:
        client = _get_client()
        result = client.rollback(batch_id=batch_id)
        if "error" in result:
            return f"Error: {result['error']}"
        msg = result.get("message", "Rollback successful")
        return f"Rollback complete: {msg}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_command_history(
    limit: int = 20,
) -> str:
    """Get recent command execution history.

    Args:
        limit: Number of history entries to return (default 20)
    """
    try:
        client = _get_client()
        result = client.get_command_history(limit=limit)
        records = result.get("history", [])
        if not records:
            return "No command history recorded."
        lines = [f"Command History ({len(records)} entries):"]
        for i, rec in enumerate(records, 1):
            status = rec.get("status", "?")
            action = rec.get("action", "?")
            duration = rec.get("duration_ms", 0)
            error = rec.get("error", "")
            line = f"  {i}. {action} — {status} ({duration:.1f}ms)"
            if error:
                line += f" — {error}"
            lines.append(line)
        return "\n".join(lines)
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_canvas_info() -> str:
    """Get information about the current canvas including dimensions, name, and color model.

    Use this to understand the canvas you are working with.
    """
    try:
        client = _get_client()
        result = client.get_canvas_info()
        if "error" in result:
            return f"Error: {result['error']}"
        parts = []
        if "name" in result:
            parts.append(f"name={result['name']}")
        if "width" in result:
            parts.append(f"width={result['width']}")
        if "height" in result:
            parts.append(f"height={result['height']}")
        if "color_model" in result:
            parts.append(f"color_model={result['color_model']}")
        if "color_depth" in result:
            parts.append(f"color_depth={result['color_depth']}")
        return f"Canvas info: {', '.join(parts) if parts else 'no active document'}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_current_color() -> str:
    """Get the current foreground and background paint colors.

    Use this to check what colors are currently selected for painting.
    """
    try:
        client = _get_client()
        result = client.get_current_color()
        if "error" in result:
            return f"Error: {result['error']}"
        fg = result.get("foreground", "unknown")
        bg = result.get("background", "unknown")
        return f"Colors — foreground: {fg}, background: {bg}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_current_brush() -> str:
    """Get the current brush preset name, size, and opacity.

    Use this to check the active brush settings before painting.
    """
    try:
        client = _get_client()
        result = client.get_current_brush()
        if "error" in result:
            return f"Error: {result['error']}"
        parts = []
        if "preset" in result:
            parts.append(f"preset={result['preset']}")
        if "size" in result:
            parts.append(f"size={result['size']}")
        if "opacity" in result:
            parts.append(f"opacity={result['opacity']}")
        return f"Brush info: {', '.join(parts) if parts else 'no active view'}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_select_rect(x: int, y: int, width: int, height: int) -> str:
    """Select a rectangular area on the canvas.

    Args:
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of the selection
        height: Height of the selection
    """
    try:
        client = _get_client()
        result = client.select_rect(x=x, y=y, width=width, height=height)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Selected rectangle {width}x{height} at ({x}, {y})"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_select_ellipse(cx: int, cy: int, rx: int, ry: int) -> str:
    """Select an elliptical area on the canvas.

    Args:
        cx: X coordinate of center
        cy: Y coordinate of center
        rx: Horizontal radius
        ry: Vertical radius
    """
    try:
        client = _get_client()
        result = client.select_ellipse(cx=cx, cy=cy, rx=rx, ry=ry)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Selected ellipse at ({cx}, {cy}) with radii {rx}x{ry}"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_select_polygon(points: list[list[int]]) -> str:
    """Select a polygonal area on the canvas.

    Args:
        points: List of [x, y] coordinate pairs (minimum 3 points)
    """
    try:
        client = _get_client()
        result = client.select_polygon(points=points)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Selected polygon with {len(points)} points"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_selection_info() -> str:
    """Get information about the current selection."""
    try:
        client = _get_client()
        result = client.selection_info()
        if "error" in result:
            return f"Error: {result['error']}"
        if result.get("has_selection"):
            b: dict = result.get("bounds", {}) or {}
            return f"Selection: x={b.get('x')}, y={b.get('y')}, w={b.get('width')}, h={b.get('height')}"
        return "No active selection"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_clear_selection() -> str:
    """Clear the content of the current selection."""
    try:
        client = _get_client()
        result = client.clear_selection()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Cleared selection"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_invert_selection() -> str:
    """Invert the current selection."""
    try:
        client = _get_client()
        result = client.invert_selection()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Inverted selection"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_fill_selection() -> str:
    """Fill the current selection with the foreground color."""
    try:
        client = _get_client()
        result = client.fill_selection()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Filled selection"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_deselect() -> str:
    """Remove the current selection."""
    try:
        client = _get_client()
        result = client.deselect()
        if "error" in result:
            return f"Error: {result['error']}"
        return "Deselected"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_get_capabilities() -> str:
    """Get detected API capabilities from the Krita plugin."""
    try:
        client = _get_client()
        result = client.get_capabilities()
        if "error" in result:
            return f"Error: {result['error']}"
        caps = result.get("capabilities", {})
        available = result.get("selection_tools", [])
        if available:
            return f"Available selection tools: {', '.join(available)}"
        return "No selection tools detected in this Krita version"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_transform_selection(
    dx: int = 0,
    dy: int = 0,
    angle: float = 0.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
) -> str:
    """Transform the current selection (move, rotate, scale).

    Args:
        dx: Horizontal offset in pixels
        dy: Vertical offset in pixels
        angle: Rotation angle in degrees
        scale_x: Horizontal scale factor
        scale_y: Vertical scale factor
    """
    try:
        client = _get_client()
        result = client.transform_selection(dx=dx, dy=dy, angle=angle, scale_x=scale_x, scale_y=scale_y)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Transformed selection (dx={dx}, dy={dy}, angle={angle}°)"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_grow_selection(pixels: int) -> str:
    """Grow the current selection outward by N pixels."""
    try:
        client = _get_client()
        result = client.grow_selection(pixels)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Grew selection by {pixels}px"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_shrink_selection(pixels: int) -> str:
    """Shrink the current selection inward by N pixels."""
    try:
        client = _get_client()
        result = client.shrink_selection(pixels)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Shrunk selection by {pixels}px"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_border_selection(pixels: int) -> str:
    """Create a border selection around the current selection."""
    try:
        client = _get_client()
        result = client.border_selection(pixels)
        if "error" in result:
            return f"Error: {result['error']}"
        return f"Created {pixels}px border around selection"
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_security_status() -> str:
    """Get current security limits and usage from the Krita plugin."""
    try:
        client = _get_client()
        result = client.get_security_status()
        if "error" in result:
            return f"Error: {result['error']}"
        rl = result.get("rate_limit", {})
        parts = [
            f"Rate limit: {rl.get('current_usage', 0)}/{rl.get('max_commands_per_minute', '?')} per minute",
            f"Payload limit: {result.get('payload_limit', '?') / (1024*1024):.0f}MB",
            f"Batch limit: {result.get('batch_size_limit', '?')} commands",
            f"Max canvas: {result.get('max_canvas_dim', '?')}x{result.get('max_canvas_dim', '?')}",
        ]
        return "Security status: " + " | ".join(parts)
    except KritaError as exc:
        return _format_error(exc)


@mcp.tool()
def krita_list_tools() -> str:
    """List all available Krita MCP tools with descriptions."""
    tools = [
        ("krita_health", "Check Krita + plugin status"),
        ("krita_new_canvas", "Create canvas (width, height, bg color)"),
        ("krita_set_color", "Set foreground color (hex)"),
        ("krita_set_brush", "Set brush preset/size/opacity"),
        ("krita_stroke", "Paint stroke through [x, y] points"),
        ("krita_fill", "Fill circular area"),
        ("krita_draw_shape", "Draw rectangle/ellipse/line"),
        ("krita_get_canvas", "Export canvas to PNG"),
        ("krita_save", "Save canvas to file"),
        ("krita_undo", "Undo last action"),
        ("krita_redo", "Redo last action"),
        ("krita_clear", "Clear canvas"),
        ("krita_get_color_at", "Eyedropper - get color at pixel"),
        ("krita_list_brushes", "List brush presets"),
        ("krita_open_file", "Open existing file"),
        ("krita_batch", "Execute multiple commands sequentially"),
        ("krita_rollback", "Roll back a batch operation"),
        ("krita_select_rect", "Select a rectangular area"),
        ("krita_select_ellipse", "Select an elliptical area"),
        ("krita_select_polygon", "Select a polygonal area"),
        ("krita_selection_info", "Get current selection bounds"),
        ("krita_invert_selection", "Invert the current selection"),
        ("krita_clear_selection", "Clear selection contents"),
        ("krita_fill_selection", "Fill selection with foreground color"),
        ("krita_deselect", "Remove current selection"),
        ("krita_transform_selection", "Move/rotate/scale selection"),
        ("krita_grow_selection", "Grow selection by N pixels"),
        ("krita_shrink_selection", "Shrink selection by N pixels"),
        ("krita_border_selection", "Create border around selection"),
        ("krita_get_capabilities", "Get detected API capabilities"),
        ("krita_security_status", "Get security limits and usage"),
        ("krita_list_tools", "List all available MCP tools"),
    ]
    lines = [f"- **{name}**: {desc}" for name, desc in tools]
    return f"Available Krita MCP tools ({len(tools)} total):\n" + "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
