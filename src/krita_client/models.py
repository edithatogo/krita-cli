"""Pydantic models for all Krita MCP commands."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, field_validator

# -- Error models -------------------------------------------------------------


class ErrorCode(str, Enum):
    """Semantic error codes for plugin errors."""

    NO_ACTIVE_DOCUMENT = "NO_ACTIVE_DOCUMENT"
    NO_ACTIVE_LAYER = "NO_ACTIVE_LAYER"
    NO_ACTIVE_VIEW = "NO_ACTIVE_VIEW"
    INVALID_COLOR = "INVALID_COLOR"
    CANVAS_TOO_LARGE = "CANVAS_TOO_LARGE"
    PATH_TRAVERSAL_BLOCKED = "PATH_TRAVERSAL_BLOCKED"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PLUGIN_UNREACHABLE = "PLUGIN_UNREACHABLE"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    INVALID_SHAPE = "INVALID_SHAPE"
    LAYER_NOT_FOUND = "LAYER_NOT_FOUND"
    BRUSH_NOT_FOUND = "BRUSH_NOT_FOUND"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"
    UNKNOWN_ACTION = "UNKNOWN_ACTION"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INCOMPATIBLE_PROTOCOL = "INCOMPATIBLE_PROTOCOL"


class KritaErrorResponse(BaseModel):
    """Structured error response from the plugin."""

    code: ErrorCode
    message: str
    recoverable: bool = False


# -- Command models -----------------------------------------------------------


class NewCanvasParams(BaseModel):
    """Parameters for creating a new canvas."""

    width: Annotated[int, Field(ge=1, le=8192)] = 800
    height: Annotated[int, Field(ge=1, le=8192)] = 600
    name: str = "New Canvas"
    background: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")] = "#1a1a2e"


class SetColorParams(BaseModel):
    """Parameters for setting the foreground color."""

    color: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")]


class SetBrushParams(BaseModel):
    """Parameters for setting brush properties."""

    preset: str | None = None
    size: Annotated[int | None, Field(ge=1, le=5000)] = None
    opacity: Annotated[float | None, Field(ge=0.0, le=1.0)] = None


class StrokeParams(BaseModel):
    """Parameters for painting a stroke."""

    points: Annotated[list[list[int]], Field(min_length=2)]
    pressure: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    size: Annotated[int | None, Field(ge=1, le=5000)] = None
    hardness: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    opacity: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0

    @field_validator("points")
    @classmethod
    def validate_points(cls, value: list[list[int]]) -> list[list[int]]:
        for i, pt in enumerate(value):
            if len(pt) != 2:
                msg = f"Point {i} must have exactly 2 coordinates, got {len(pt)}."
                raise ValueError(msg)
        return value


class FillParams(BaseModel):
    """Parameters for filling a circular area."""

    x: int
    y: int
    radius: Annotated[int, Field(ge=1, le=5000)] = 50


class DrawShapeParams(BaseModel):
    """Parameters for drawing a shape."""

    shape: Literal["rectangle", "ellipse", "line"]
    x: int
    y: int
    width: int = 100
    height: int = 100
    fill: bool = True
    stroke: bool = False
    x2: int | None = None
    y2: int | None = None
    line_width: int = 2


class GetCanvasParams(BaseModel):
    """Parameters for exporting the canvas."""

    filename: str = "canvas.png"


class UndoParams(BaseModel):
    """Parameters for undo (empty)."""


class RedoParams(BaseModel):
    """Parameters for redo (empty)."""


class ClearParams(BaseModel):
    """Parameters for clearing the canvas."""

    color: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")] = "#1a1a2e"


class SaveParams(BaseModel):
    """Parameters for saving the canvas."""

    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value or not value.strip():
            msg = "Path cannot be empty."
            raise ValueError(msg)
        if ".." in value:
            msg = "Path traversal is not allowed."
            raise ValueError(msg)
        return value.strip()


class GetColorAtParams(BaseModel):
    """Parameters for sampling a pixel color."""

    x: int
    y: int


class ListBrushesParams(BaseModel):
    """Parameters for listing brush presets."""

    filter: str = ""
    limit: Annotated[int, Field(ge=1, le=500)] = 20


class OpenFileParams(BaseModel):
    """Parameters for opening a file."""

    path: str

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value or not value.strip():
            msg = "Path cannot be empty."
            raise ValueError(msg)
        if ".." in value:
            msg = "Path traversal is not allowed."
            raise ValueError(msg)
        return value.strip()


class CanvasInfoParams(BaseModel):
    """Parameters for getting canvas information."""


class CurrentColorParams(BaseModel):
    """Parameters for getting the current color."""


class CurrentBrushParams(BaseModel):
    """Parameters for getting the current brush."""


class ListLayersParams(BaseModel):
    """Parameters for listing layers."""


class CreateLayerParams(BaseModel):
    """Parameters for creating a new layer."""

    name: str = "New Layer"
    layer_type: str = "paintlayer"


class SelectLayerParams(BaseModel):
    """Parameters for selecting a layer by name."""

    name: str


class DeleteLayerParams(BaseModel):
    """Parameters for deleting a layer by name."""

    name: str


class RenameLayerParams(BaseModel):
    """Parameters for renaming a layer."""

    old_name: str
    new_name: str


class SetLayerOpacityParams(BaseModel):
    """Parameters for setting layer opacity."""

    name: str
    opacity: Annotated[float, Field(ge=0.0, le=1.0)]


class SetLayerVisibilityParams(BaseModel):
    """Parameters for toggling layer visibility."""

    name: str
    visible: bool


# -- Selection operations -----------------------------------------------------


class SelectAreaParams(BaseModel):
    """Parameters for selecting a rectangular area."""

    x: int
    y: int
    width: Annotated[int, Field(ge=1, le=8192)]
    height: Annotated[int, Field(ge=1, le=8192)]


class ClearSelectionParams(BaseModel):
    """Parameters for clearing the current selection (empty)."""


class FillSelectionParams(BaseModel):
    """Parameters for filling the current selection (empty)."""


class DeselectParams(BaseModel):
    """Parameters for deselecting (empty)."""


# -- Batch operations ---------------------------------------------------------


class BatchCommand(BaseModel):
    """A single command within a batch."""

    action: str
    params: dict[str, Any] = {}


class BatchParams(BaseModel):
    """Parameters for batch execution."""

    commands: Annotated[list[BatchCommand], Field(min_length=1)]


# -- Command registry ---------------------------------------------------------

COMMAND_MODELS: dict[str, type[BaseModel]] = {
    "new_canvas": NewCanvasParams,
    "set_color": SetColorParams,
    "set_brush": SetBrushParams,
    "stroke": StrokeParams,
    "fill": FillParams,
    "draw_shape": DrawShapeParams,
    "get_canvas": GetCanvasParams,
    "undo": UndoParams,
    "redo": RedoParams,
    "clear": ClearParams,
    "save": SaveParams,
    "get_color_at": GetColorAtParams,
    "list_brushes": ListBrushesParams,
    "open_file": OpenFileParams,
    "batch": BatchParams,
    "list_layers": ListLayersParams,
    "create_layer": CreateLayerParams,
    "select_layer": SelectLayerParams,
    "delete_layer": DeleteLayerParams,
    "rename_layer": RenameLayerParams,
    "set_layer_opacity": SetLayerOpacityParams,
    "set_layer_visibility": SetLayerVisibilityParams,
    "get_canvas_info": CanvasInfoParams,
    "get_current_color": CurrentColorParams,
    "get_current_brush": CurrentBrushParams,
    "select_area": SelectAreaParams,
    "clear_selection": ClearSelectionParams,
    "fill_selection": FillSelectionParams,
    "deselect": DeselectParams,
}
