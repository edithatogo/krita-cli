"""Unit tests for krita_client.models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import (
    BatchCommand,
    BatchParams,
    ClearParams,
    DrawShapeParams,
    FillParams,
    GetCanvasParams,
    GetColorAtParams,
    ListBrushesParams,
    NewCanvasParams,
    OpenFileParams,
    RedoParams,
    SaveParams,
    SetBrushParams,
    SetColorParams,
    StrokeParams,
    UndoParams,
)

# -- NewCanvasParams ----------------------------------------------------------


def test_new_canvas_defaults() -> None:
    params = NewCanvasParams()
    assert params.width == 800
    assert params.height == 600
    assert params.name == "New Canvas"
    assert params.background == "#1a1a2e"


def test_new_canvas_custom() -> None:
    params = NewCanvasParams(width=1920, height=1080, background="#ffffff")
    assert params.width == 1920
    assert params.height == 1080
    assert params.background == "#ffffff"


def test_new_canvas_invalid_color() -> None:
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        NewCanvasParams(background="not-a-color")


def test_new_canvas_too_large() -> None:
    with pytest.raises(ValidationError):
        NewCanvasParams(width=10000)


def test_new_canvas_zero_dimension() -> None:
    with pytest.raises(ValidationError):
        NewCanvasParams(width=0)


# -- SetColorParams -----------------------------------------------------------


def test_set_color_valid() -> None:
    params = SetColorParams(color="#ff6b6b")
    assert params.color == "#ff6b6b"


def test_set_color_with_alpha() -> None:
    params = SetColorParams(color="#ff6b6b80")
    assert params.color == "#ff6b6b80"


def test_set_color_invalid() -> None:
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        SetColorParams(color="#gggggg")


def test_set_color_no_hash() -> None:
    with pytest.raises(ValidationError):
        SetColorParams(color="ff6b6b")


# -- SetBrushParams -----------------------------------------------------------


def test_set_brush_defaults() -> None:
    params = SetBrushParams()
    assert params.preset is None
    assert params.size is None
    assert params.opacity is None


def test_set_brush_all() -> None:
    params = SetBrushParams(preset="Soft", size=50, opacity=0.8)
    assert params.preset == "Soft"
    assert params.size == 50
    assert params.opacity == 0.8


def test_set_brush_invalid_size() -> None:
    with pytest.raises(ValidationError):
        SetBrushParams(size=0)


def test_set_brush_invalid_opacity() -> None:
    with pytest.raises(ValidationError):
        SetBrushParams(opacity=1.5)


# -- StrokeParams -------------------------------------------------------------


def test_stroke_valid() -> None:
    params = StrokeParams(points=[[0, 0], [100, 100], [200, 50]])
    assert len(params.points) == 3


def test_stroke_too_few_points() -> None:
    with pytest.raises(ValidationError, match="too_short"):
        StrokeParams(points=[[0, 0]])


def test_stroke_invalid_point() -> None:
    with pytest.raises(ValidationError):
        StrokeParams(points=[[0, 0], [100]])


def test_stroke_defaults() -> None:
    params = StrokeParams(points=[[0, 0], [100, 100]])
    assert params.pressure == 1.0
    assert params.hardness == 0.5
    assert params.opacity == 1.0
    assert params.size is None


# -- FillParams ---------------------------------------------------------------


def test_fill_valid() -> None:
    params = FillParams(x=100, y=200, radius=75)
    assert params.x == 100
    assert params.y == 200
    assert params.radius == 75


def test_fill_invalid_radius() -> None:
    with pytest.raises(ValidationError):
        FillParams(x=0, y=0, radius=0)


# -- DrawShapeParams ----------------------------------------------------------


def test_draw_shape_rectangle() -> None:
    params = DrawShapeParams(shape="rectangle", x=0, y=0)
    assert params.shape == "rectangle"
    assert params.fill is True


def test_draw_shape_line() -> None:
    params = DrawShapeParams(shape="line", x=0, y=0, x2=100, y2=100)
    assert params.shape == "line"
    assert params.x2 == 100


def test_draw_shape_invalid_type() -> None:
    with pytest.raises(ValidationError):
        DrawShapeParams(shape="triangle", x=0, y=0)


# -- GetCanvasParams ----------------------------------------------------------


def test_get_canvas_defaults() -> None:
    params = GetCanvasParams()
    assert params.filename == "canvas.png"


# -- UndoParams / RedoParams --------------------------------------------------


def test_undo_params() -> None:
    UndoParams()


def test_redo_params() -> None:
    RedoParams()


# -- ClearParams --------------------------------------------------------------


def test_clear_defaults() -> None:
    params = ClearParams()
    assert params.color == "#1a1a2e"


def test_clear_custom_color() -> None:
    params = ClearParams(color="#000000")
    assert params.color == "#000000"


# -- SaveParams ---------------------------------------------------------------


def test_save_valid() -> None:
    params = SaveParams(path="/tmp/test.png")
    assert params.path == "/tmp/test.png"


def test_save_path_traversal() -> None:
    with pytest.raises(ValidationError, match="Path traversal"):
        SaveParams(path="../../etc/passwd")


def test_save_empty_path() -> None:
    with pytest.raises(ValidationError, match="cannot be empty"):
        SaveParams(path="")


# -- GetColorAtParams ---------------------------------------------------------


def test_get_color_at() -> None:
    params = GetColorAtParams(x=50, y=100)
    assert params.x == 50
    assert params.y == 100


# -- ListBrushesParams --------------------------------------------------------


def test_list_brushes_defaults() -> None:
    params = ListBrushesParams()
    assert params.filter == ""
    assert params.limit == 20


def test_list_brushes_custom() -> None:
    params = ListBrushesParams(filter="soft", limit=10)
    assert params.filter == "soft"
    assert params.limit == 10


# -- OpenFileParams -----------------------------------------------------------


def test_open_file_valid() -> None:
    params = OpenFileParams(path="/tmp/test.kra")
    assert params.path == "/tmp/test.kra"


def test_open_file_path_traversal() -> None:
    with pytest.raises(ValidationError, match="Path traversal"):
        OpenFileParams(path="../secret.kra")


def test_open_file_empty() -> None:
    with pytest.raises(ValidationError, match="cannot be empty"):
        OpenFileParams(path="")


# -- BatchParams --------------------------------------------------------------


def test_batch_valid() -> None:
    params = BatchParams(
        commands=[
            BatchCommand(action="set_color", params={"color": "#ff0000"}),
            BatchCommand(action="stroke", params={"points": [[0, 0], [100, 100]]}),
        ],
    )
    assert len(params.commands) == 2


def test_batch_empty() -> None:
    with pytest.raises(ValidationError):
        BatchParams(commands=[])


# -- COMMAND_MODELS registry --------------------------------------------------


def test_command_models_registry() -> None:
    from krita_client.models import COMMAND_MODELS

    expected_actions = {
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
        "list_layers",
        "create_layer",
        "select_layer",
        "delete_layer",
        "rename_layer",
        "set_layer_opacity",
        "set_layer_visibility",
        "get_canvas_info",
        "get_current_color",
        "get_current_brush",
        "select_rect",
        "select_ellipse",
        "select_polygon",
        "selection_info",
        "get_capabilities",
        "clear_selection",
        "invert_selection",
        "fill_selection",
        "deselect",
        "transform_selection",
        "grow_selection",
        "shrink_selection",
        "border_selection",
        "combine_selections",
        "get_command_history",
        "rollback",
    }
    assert set(COMMAND_MODELS.keys()) == expected_actions
