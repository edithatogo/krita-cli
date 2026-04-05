"""Krita CLI — Compatibility shim.

All functionality has moved to krita_cli.app.
This module re-exports everything for backward compatibility.
"""

from krita_cli.app import (
    CLIState,
    _format_result,
    _get_client,
    _handle_error,
    app,
    call,
    callback,
    clear,
    console,
    draw_shape,
    fill,
    get_canvas,
    get_color_at,
    health,
    list_brushes,
    main,
    new_canvas,
    open_file,
    redo,
    save,
    set_brush,
    set_color,
    stroke,
    undo,
)

__all__ = [
    "CLIState",
    "_format_result",
    "_get_client",
    "_handle_error",
    "app",
    "call",
    "callback",
    "clear",
    "console",
    "draw_shape",
    "fill",
    "get_canvas",
    "get_color_at",
    "health",
    "list_brushes",
    "main",
    "new_canvas",
    "open_file",
    "redo",
    "save",
    "set_brush",
    "set_color",
    "stroke",
    "undo",
]
