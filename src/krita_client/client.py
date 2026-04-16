"""Typed HTTP client for communicating with the Krita plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from krita_client.config import ClientConfig
from krita_client.models import (
    COMMAND_MODELS,
    BatchParams,
    ClearParams,
    CreateLayerParams,
    DeleteLayerParams,
    DrawShapeParams,
    ErrorCode,
    FillParams,
    GetCanvasParams,
    GetColorAtParams,
    ListBrushesParams,
    ListLayersParams,
    NewCanvasParams,
    OpenFileParams,
    RenameLayerParams,
    RollbackParams,
    SaveParams,
    SelectLayerParams,
    SetBrushParams,
    SetColorParams,
    SetLayerOpacityParams,
    SetLayerVisibilityParams,
    StrokeParams,
)

if TYPE_CHECKING:
    from typing import Self

from pydantic import BaseModel

MIN_PROTOCOL_VERSION = "1.0.0"
MAX_PROTOCOL_VERSION = "1.0.0"
_SUPPORTED_PROTOCOL_VERSION = 1
_CANNOT_CONNECT_MSG = "Cannot connect to Krita. Is Krita running with the MCP plugin enabled?"


class KritaError(Exception):
    """Base exception for Krita client errors."""

    def __init__(self, message: str, code: ErrorCode | None = None, recoverable: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable


class KritaConnectionError(KritaError):
    """Raised when the Krita plugin is unreachable."""


class KritaCommandError(KritaError):
    """Raised when a command execution fails."""


class KritaValidationError(KritaError):
    """Raised when command parameters fail validation."""


class KritaClient:
    """Typed HTTP client for the Krita MCP plugin.

    All public methods correspond to a Krita plugin action.
    Parameters are validated via pydantic models before being sent.
    """

    def __init__(self, config: ClientConfig | None = None) -> None:
        self._config = config or ClientConfig()
        self._client = httpx.Client(
            base_url=self._config.url,
            timeout=httpx.Timeout(
                connect=5.0,
                read=self._config.default_timeout,
                write=self._config.default_timeout,
                pool=5.0,
            ),
        )

    @property
    def config(self) -> ClientConfig:
        return self._config

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # -- Internal helpers -----------------------------------------------------

    def _send(
        self,
        action: str,
        params: dict[str, object] | None = None,
        timeout: float | None = None,
    ) -> dict[str, object]:
        """Send a command to the Krita plugin and return the JSON response."""
        body: dict[str, object] = {"action": action, "params": params or {}}
        request_timeout = timeout or self._config.default_timeout

        try:
            response = self._client.post(
                "/",
                json=body,
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=request_timeout,
                    write=request_timeout,
                    pool=5.0,
                ),
            )
            data = response.json()
            if "error" in data:
                err = data["error"]
                if isinstance(err, dict):
                    msg = err.get("message", "Unknown error")
                    code = err.get("code")
                    recov = err.get("recoverable", False)
                    raise KritaCommandError(msg, code=code, recoverable=recov)
                raise KritaCommandError(str(err))
            return data  # type: ignore[no-any-return]
        except httpx.ConnectError as exc:
            raise KritaConnectionError(
                _CANNOT_CONNECT_MSG, code=ErrorCode.PLUGIN_UNREACHABLE, recoverable=True
            ) from exc
        except httpx.HTTPStatusError as exc:
            msg = f"HTTP {exc.response.status_code}: {exc.response.text}"
            raise KritaCommandError(msg, code=ErrorCode.INTERNAL_ERROR) from exc
        except httpx.HTTPError as exc:
            raise KritaCommandError(str(exc), code=ErrorCode.COMMAND_TIMEOUT, recoverable=True) from exc

    def _is_compatible(self, protocol_version: str) -> bool:
        """Check if a protocol version string is within the supported range."""
        try:
            parts = protocol_version.split(".")
            if len(parts) != 3:
                return False
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            min_parts = MIN_PROTOCOL_VERSION.split(".")
            max_parts = MAX_PROTOCOL_VERSION.split(".")
            min_tuple = (int(min_parts[0]), int(min_parts[1]), int(min_parts[2]))
            max_tuple = (int(max_parts[0]), int(max_parts[1]), int(max_parts[2]))
            return min_tuple <= (major, minor, patch) <= max_tuple
        except (ValueError, IndexError):
            return False

    def _health_get(self) -> dict[str, object]:
        """Send a GET request to the health endpoint."""
        try:
            response = self._client.get(
                "/health",
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=self._config.health_timeout,
                    write=5.0,
                    pool=5.0,
                ),
            )
            data = response.json()  # type: ignore[no-any-return]
            protocol_version = data.get("protocol_version")
            if protocol_version is not None:
                if isinstance(protocol_version, int) and protocol_version > _SUPPORTED_PROTOCOL_VERSION:
                    raise KritaConnectionError(
                        f"Plugin protocol mismatch. Client expects v{_SUPPORTED_PROTOCOL_VERSION} "
                        f"but plugin is running v{protocol_version}. Please upgrade krita-cli.",
                        code=ErrorCode.INCOMPATIBLE_PROTOCOL,
                        recoverable=True,
                    )
                if isinstance(protocol_version, str) and not self._is_compatible(protocol_version):
                    raise KritaConnectionError(
                        f"Incompatible protocol version: {protocol_version}. "
                        f"Expected {MIN_PROTOCOL_VERSION}-{MAX_PROTOCOL_VERSION}",
                        code=ErrorCode.INCOMPATIBLE_PROTOCOL,
                        recoverable=True,
                    )
            return data
        except httpx.ConnectError as exc:
            raise KritaConnectionError(
                _CANNOT_CONNECT_MSG, code=ErrorCode.PLUGIN_UNREACHABLE, recoverable=True
            ) from exc

    def _validate(
        self,
        model_cls: type[BaseModel],
        params: dict[str, object],
    ) -> dict[str, object]:
        """Validate params against a pydantic model and return the validated dict."""
        try:
            instance = model_cls.model_validate(params)
            return instance.model_dump(exclude_none=True)
        except Exception as exc:
            raise KritaValidationError(str(exc)) from exc

    # -- Public API -----------------------------------------------------------

    def health(self) -> dict[str, object]:
        """Check if Krita is running and the plugin is active."""
        return self._health_get()

    def new_canvas(
        self,
        *,
        width: int = 800,
        height: int = 600,
        name: str = "New Canvas",
        background: str = "#1a1a2e",
    ) -> dict[str, object]:
        """Create a new canvas in Krita."""
        validated = self._validate(
            NewCanvasParams,
            {"width": width, "height": height, "name": name, "background": background},
        )
        return self._send("new_canvas", validated)

    def set_color(self, *, color: str) -> dict[str, object]:
        """Set the foreground paint color."""
        validated = self._validate(SetColorParams, {"color": color})
        return self._send("set_color", validated)

    def set_brush(
        self,
        *,
        preset: str | None = None,
        size: int | None = None,
        opacity: float | None = None,
    ) -> dict[str, object]:
        """Set brush preset and properties."""
        validated = self._validate(
            SetBrushParams,
            {"preset": preset, "size": size, "opacity": opacity},
        )
        return self._send("set_brush", validated)

    def stroke(
        self,
        points: list[list[int]],
        *,
        pressure: float = 1.0,
        size: int | None = None,
        hardness: float = 0.5,
        opacity: float = 1.0,
    ) -> dict[str, object]:
        """Paint a stroke through a series of points."""
        validated = self._validate(
            StrokeParams,
            {
                "points": points,
                "pressure": pressure,
                "size": size,
                "hardness": hardness,
                "opacity": opacity,
            },
        )
        return self._send("stroke", validated)

    def fill(self, x: int, y: int, *, radius: int = 50) -> dict[str, object]:
        """Fill a circular area at a point."""
        validated = self._validate(FillParams, {"x": x, "y": y, "radius": radius})
        return self._send("fill", validated)

    def draw_shape(
        self,
        shape: str,
        x: int,
        y: int,
        *,
        width: int = 100,
        height: int = 100,
        fill: bool = True,
        stroke: bool = False,
        x2: int | None = None,
        y2: int | None = None,
        line_width: int = 2,
    ) -> dict[str, object]:
        """Draw a shape on the canvas."""
        validated = self._validate(
            DrawShapeParams,
            {
                "shape": shape,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "fill": fill,
                "stroke": stroke,
                "x2": x2,
                "y2": y2,
                "line_width": line_width,
            },
        )
        return self._send("draw_shape", validated)

    def get_canvas(self, *, filename: str = "canvas.png") -> dict[str, object]:
        """Export current canvas to a PNG file."""
        validated = self._validate(GetCanvasParams, {"filename": filename})
        return self._send("get_canvas", validated, timeout=self._config.export_timeout)

    def undo(self) -> dict[str, object]:
        """Undo the last action."""
        return self._send("undo", {})

    def redo(self) -> dict[str, object]:
        """Redo the last undone action."""
        return self._send("redo", {})

    def clear(self, *, color: str = "#1a1a2e") -> dict[str, object]:
        """Clear the canvas to a solid color."""
        validated = self._validate(ClearParams, {"color": color})
        return self._send("clear", validated)

    def save(self, path: str) -> dict[str, object]:
        """Save the current canvas to a specific file path."""
        validated = self._validate(SaveParams, {"path": path})
        return self._send("save", validated, timeout=self._config.export_timeout)

    def get_color_at(self, x: int, y: int) -> dict[str, object]:
        """Sample the color at a specific pixel."""
        validated = self._validate(GetColorAtParams, {"x": x, "y": y})
        return self._send("get_color_at", validated)

    def list_brushes(self, *, filter: str = "", limit: int = 20) -> dict[str, object]:  # noqa: A002
        """List available brush presets."""
        validated = self._validate(ListBrushesParams, {"filter": filter, "limit": limit})
        return self._send("list_brushes", validated)

    def open_file(self, path: str) -> dict[str, object]:
        """Open an existing file in Krita."""
        validated = self._validate(OpenFileParams, {"path": path})
        return self._send("open_file", validated)

    def batch_execute(self, commands: list[dict[str, object]], *, stop_on_error: bool = False) -> dict[str, object]:
        """Execute multiple commands in a single batch.

        Args:
            commands: List of command dicts, each with "action" and "params" keys.
            stop_on_error: Stop executing remaining commands on first error.

        Returns:
            Dict with keys:
            - "status": "ok" (all succeeded), "partial" (some failed), or "error" (all failed)
            - "results": List of per-command results with "action", "status", and "result"/"error"
            - "count": Number of commands executed
        """
        validated = self._validate(BatchParams, {"commands": commands, "stop_on_error": stop_on_error})
        return self._send("batch", validated)

    def batch(self, commands: list[dict[str, object]], *, stop_on_error: bool = False) -> dict[str, object]:
        """Execute multiple commands in a single batch (alias for batch_execute)."""
        return self.batch_execute(commands, stop_on_error=stop_on_error)

    def get_command_history(self, *, limit: int = 20) -> dict[str, object]:
        """Retrieve recent command execution history."""
        return self._send("get_command_history", {"limit": limit})

    def rollback(self, batch_id: str) -> dict[str, object]:
        """Roll back a batch execution.

        Args:
            batch_id: The unique ID of the batch to roll back.

        Returns:
            Dict with keys:
            - "status": "ok" or "error"
            - "message": Optional error message
        """
        validated = self._validate(RollbackParams, {"batch_id": batch_id})
        return self._send("rollback", validated)

    def get_canvas_info(self) -> dict[str, object]:
        """Get information about the current canvas."""
        return self._send("get_canvas_info", {})

    def get_current_color(self) -> dict[str, object]:
        """Get the current foreground and background colors."""
        return self._send("get_current_color", {})

    def get_current_brush(self) -> dict[str, object]:
        """Get the current brush preset and properties."""
        return self._send("get_current_brush", {})

    def select_rect(
        self,
        x: int,
        y: int,
        *,
        width: int,
        height: int,
    ) -> dict[str, object]:
        """Select a rectangular area on the canvas."""
        from krita_client.models import SelectRectParams

        validated = self._validate(
            SelectRectParams,
            {"x": x, "y": y, "width": width, "height": height},
        )
        return self._send("select_rect", validated)

    def select_ellipse(
        self,
        cx: int,
        cy: int,
        *,
        rx: int,
        ry: int,
    ) -> dict[str, object]:
        """Select an elliptical area on the canvas."""
        from krita_client.models import SelectEllipseParams

        validated = self._validate(
            SelectEllipseParams,
            {"cx": cx, "cy": cy, "rx": rx, "ry": ry},
        )
        return self._send("select_ellipse", validated)

    def select_polygon(
        self,
        points: list[list[int]],
    ) -> dict[str, object]:
        """Select a polygonal area on the canvas."""
        from krita_client.models import SelectPolygonParams

        validated = self._validate(SelectPolygonParams, {"points": points})
        return self._send("select_polygon", validated)

    def selection_info(self) -> dict[str, object]:
        """Get information about the current selection."""
        return self._send("selection_info", {})

    def get_capabilities(self) -> dict[str, object]:
        """Get detected API capabilities from the plugin."""
        return self._send("get_capabilities", {})

    def get_security_status(self) -> dict[str, object]:
        """Get current security limits and usage from the plugin."""
        return self._send("get_security_status", {})

    def transform_selection(
        self,
        *,
        dx: int = 0,
        dy: int = 0,
        angle: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
    ) -> dict[str, object]:
        """Transform the current selection (move, rotate, scale)."""
        from krita_client.models import TransformSelectionParams

        validated = self._validate(
            TransformSelectionParams,
            {"dx": dx, "dy": dy, "angle": angle, "scale_x": scale_x, "scale_y": scale_y},
        )
        return self._send("transform_selection", validated)

    def grow_selection(self, pixels: int) -> dict[str, object]:
        """Grow the current selection outward by N pixels."""
        from krita_client.models import ModifySelectionParams

        validated = self._validate(ModifySelectionParams, {"pixels": pixels})
        return self._send("grow_selection", validated)

    def shrink_selection(self, pixels: int) -> dict[str, object]:
        """Shrink the current selection inward by N pixels."""
        from krita_client.models import ModifySelectionParams

        validated = self._validate(ModifySelectionParams, {"pixels": pixels})
        return self._send("shrink_selection", validated)

    def border_selection(self, pixels: int) -> dict[str, object]:
        """Create a border selection of N pixels around the current selection."""
        from krita_client.models import ModifySelectionParams

        validated = self._validate(ModifySelectionParams, {"pixels": pixels})
        return self._send("border_selection", validated)

    def combine_selections(
        self,
        operation: str,
    ) -> dict[str, object]:
        """Combine selections using union, intersect, or subtract."""
        from krita_client.models import CombineSelectionParams

        validated = self._validate(CombineSelectionParams, {"operation": operation})
        return self._send("combine_selections", validated)

    def clear_selection(self) -> dict[str, object]:
        """Clear the current selection."""
        return self._send("clear_selection", {})

    def invert_selection(self) -> dict[str, object]:
        """Invert the current selection."""
        return self._send("invert_selection", {})

    def fill_selection(self) -> dict[str, object]:
        """Fill the current selection with the foreground color."""
        return self._send("fill_selection", {})

    def deselect(self) -> dict[str, object]:
        """Remove the current selection."""
        return self._send("deselect", {})

    def select_by_color(
        self,
        *,
        x: int | None = None,
        y: int | None = None,
        tolerance: float = 0.1,
        contiguous: bool = True,
    ) -> dict[str, object]:
        """Select pixels by color similarity.

        Args:
            x: X coordinate for point-based selection (magic wand). None for global.
            y: Y coordinate for point-based selection (magic wand). None for global.
            tolerance: Color tolerance (0.0-1.0).
            contiguous: If True, only select contiguous region (magic wand).
                       If False, select all matching pixels globally.
        """
        from krita_client.models import SelectByColorParams

        params: dict[str, object] = {"tolerance": tolerance, "contiguous": contiguous}
        if x is not None and y is not None:
            params["x"] = x
            params["y"] = y
        validated = self._validate(SelectByColorParams, params)
        return self._send("select_by_color", validated)

    def select_by_alpha(
        self,
        *,
        min_alpha: int = 1,
        max_alpha: int = 255,
    ) -> dict[str, object]:
        """Select pixels by alpha value range.

        Args:
            min_alpha: Minimum alpha value (0-255).
            max_alpha: Maximum alpha value (0-255).
        """
        from krita_client.models import SelectByAlphaParams

        validated = self._validate(SelectByAlphaParams, {"min_alpha": min_alpha, "max_alpha": max_alpha})
        return self._send("select_by_alpha", validated)

    def save_selection(
        self,
        path: str,
        *,
        format: str = "png",  # noqa: A002
    ) -> dict[str, object]:
        """Save current selection to a file as a mask.

        Args:
            path: File path to save selection mask.
            format: Image format (default: png).
        """
        from krita_client.models import SaveSelectionParams

        validated = self._validate(SaveSelectionParams, {"path": path, "format": format})
        return self._send("save_selection", validated)

    def load_selection(
        self,
        path: str,
    ) -> dict[str, object]:
        """Load selection from a mask file.

        Args:
            path: File path to load selection mask from.
        """
        from krita_client.models import LoadSelectionParams

        validated = self._validate(LoadSelectionParams, {"path": path})
        return self._send("load_selection", validated)

    def selection_stats(self) -> dict[str, object]:
        """Get statistics about the current selection.

        Returns pixel count, centroid, area percentage, etc.
        """
        return self._send("selection_stats", {})

    def save_selection_channel(self, *, name: str) -> dict[str, object]:
        """Save current selection as a named channel.

        Args:
            name: Name for the selection channel.
        """
        from krita_client.models import SelectionChannelParams

        validated = self._validate(SelectionChannelParams, {"name": name})
        return self._send("save_selection_channel", validated)

    def load_selection_channel(self, *, name: str) -> dict[str, object]:
        """Load a named selection channel.

        Args:
            name: Name of the selection channel to load.
        """
        from krita_client.models import SelectionChannelParams

        validated = self._validate(SelectionChannelParams, {"name": name})
        return self._send("load_selection_channel", validated)

    def list_selection_channels(self) -> dict[str, object]:
        """List all saved selection channels."""
        return self._send("list_selection_channels", {})

    def delete_selection_channel(self, *, name: str) -> dict[str, object]:
        """Delete a saved selection channel.

        Args:
            name: Name of the selection channel to delete.
        """
        from krita_client.models import SelectionChannelParams

        validated = self._validate(SelectionChannelParams, {"name": name})
        return self._send("delete_selection_channel", validated)

    # -- Layer management -----------------------------------------------------

    def list_layers(self) -> dict[str, object]:
        """List all layers in the current document."""
        validated = self._validate(ListLayersParams, {})
        return self._send("list_layers", validated)

    def create_layer(
        self,
        *,
        name: str = "New Layer",
        layer_type: str = "paintlayer",
    ) -> dict[str, object]:
        """Create a new layer in the current document."""
        validated = self._validate(CreateLayerParams, {"name": name, "layer_type": layer_type})
        return self._send("create_layer", validated)

    def select_layer(self, *, name: str) -> dict[str, object]:
        """Select a layer by name."""
        validated = self._validate(SelectLayerParams, {"name": name})
        return self._send("select_layer", validated)

    def delete_layer(self, *, name: str) -> dict[str, object]:
        """Delete a layer by name."""
        validated = self._validate(DeleteLayerParams, {"name": name})
        return self._send("delete_layer", validated)

    def rename_layer(self, *, old_name: str, new_name: str) -> dict[str, object]:
        """Rename a layer."""
        validated = self._validate(RenameLayerParams, {"old_name": old_name, "new_name": new_name})
        return self._send("rename_layer", validated)

    def set_layer_opacity(self, *, name: str, opacity: float) -> dict[str, object]:
        """Set the opacity of a layer."""
        validated = self._validate(SetLayerOpacityParams, {"name": name, "opacity": opacity})
        return self._send("set_layer_opacity", validated)

    def set_layer_visibility(self, *, name: str, visible: bool) -> dict[str, object]:
        """Toggle the visibility of a layer."""
        validated = self._validate(SetLayerVisibilityParams, {"name": name, "visible": visible})
        return self._send("set_layer_visibility", validated)

    # -- Generic command dispatch ---------------------------------------------

    def send_command(
        self,
        action: str,
        params: dict[str, object] | None = None,
        timeout: float | None = None,
    ) -> dict[str, object]:
        """Send an arbitrary command to the Krita plugin.

        If the action is known, params are validated against the corresponding
        pydantic model. Unknown actions are sent as-is.
        """
        model_cls = COMMAND_MODELS.get(action)
        if model_cls is not None and params is not None:
            params = self._validate(model_cls, params)
        return self._send(action, params, timeout=timeout)
