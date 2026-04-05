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


if __name__ == "__main__":  # pragma: no cover
    mcp.run()
