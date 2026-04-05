"""Typed HTTP client for communicating with the Krita plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from krita_client.config import ClientConfig
from krita_client.models import (
    COMMAND_MODELS,
    BatchParams,
    ClearParams,
    DrawShapeParams,
    FillParams,
    GetCanvasParams,
    GetColorAtParams,
    ListBrushesParams,
    NewCanvasParams,
    OpenFileParams,
    SaveParams,
    SetBrushParams,
    SetColorParams,
    StrokeParams,
)

if TYPE_CHECKING:
    from typing import Self

from pydantic import BaseModel

SUPPORTED_PROTOCOL_VERSION = 1
_CANNOT_CONNECT_MSG = "Cannot connect to Krita. Is Krita running with the MCP plugin enabled?"


class KritaError(Exception):
    """Base exception for Krita client errors."""

    def __init__(self, message: str, code: str | None = None, recoverable: bool = False) -> None:
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
            raise KritaConnectionError(_CANNOT_CONNECT_MSG) from exc
        except httpx.HTTPStatusError as exc:
            msg = f"HTTP {exc.response.status_code}: {exc.response.text}"
            code = f"HTTP_{exc.response.status_code}"
            raise KritaCommandError(msg, code=code) from exc
        except httpx.HTTPError as exc:
            raise KritaCommandError(str(exc)) from exc

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
            protocol_version = data.get("protocol_version", 0)
            if protocol_version > SUPPORTED_PROTOCOL_VERSION:
                raise KritaConnectionError(
                    f"Plugin protocol mismatch. Client expects v{SUPPORTED_PROTOCOL_VERSION} "
                    f"but plugin is running v{protocol_version}. Please upgrade krita-cli."
                )
            return data
        except httpx.ConnectError as exc:
            raise KritaConnectionError(_CANNOT_CONNECT_MSG) from exc

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

    def batch(self, commands: list[dict[str, object]]) -> dict[str, object]:
        """Execute multiple commands in a single batch."""
        validated = self._validate(BatchParams, {"commands": commands})
        return self._send("batch", validated)

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
