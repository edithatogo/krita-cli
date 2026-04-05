"""Property-based tests for krita_client models using hypothesis."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from krita_client.models import (
    ClearParams,
    DrawShapeParams,
    FillParams,
    GetColorAtParams,
    ListBrushesParams,
    NewCanvasParams,
    OpenFileParams,
    SaveParams,
    SetBrushParams,
    SetColorParams,
    StrokeParams,
)

# -- Strategy definitions ----------------------------------------------------

hex_color = st.from_regex(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$", fullmatch=True)
valid_points = st.lists(
    st.tuples(st.integers(min_value=0, max_value=10000), st.integers(min_value=0, max_value=10000)),
    min_size=2,
    max_size=100,
)
safe_path = st.text(
    alphabet=st.characters(blacklist_characters="/\\..", codec="ascii"),
    min_size=1,
    max_size=50,
).map(lambda s: f"/tmp/{s}.png")


# -- NewCanvasParams ----------------------------------------------------------


@given(
    width=st.integers(min_value=1, max_value=8192),
    height=st.integers(min_value=1, max_value=8192),
    name=st.text(min_size=1, max_size=50),
    background=hex_color,
)
@settings(max_examples=50)
def test_new_canvas_valid_inputs(width: int, height: int, name: str, background: str) -> None:
    params = NewCanvasParams(width=width, height=height, name=name, background=background)
    assert params.width == width
    assert params.height == height
    assert params.name == name
    assert params.background == background


# -- SetColorParams -----------------------------------------------------------


@given(color=hex_color)
@settings(max_examples=50)
def test_set_color_valid(color: str) -> None:
    params = SetColorParams(color=color)
    assert params.color == color


# -- StrokeParams -------------------------------------------------------------


@given(
    points=valid_points,
    pressure=st.floats(min_value=0.0, max_value=1.0),
    hardness=st.floats(min_value=0.0, max_value=1.0),
    opacity=st.floats(min_value=0.0, max_value=1.0),
)
@settings(max_examples=50)
def test_stroke_valid_inputs(
    points: list[tuple[int, int]],
    pressure: float,
    hardness: float,
    opacity: float,
) -> None:
    params = StrokeParams(
        points=[list(p) for p in points],
        pressure=pressure,
        hardness=hardness,
        opacity=opacity,
    )
    assert len(params.points) >= 2
    assert 0.0 <= params.pressure <= 1.0


# -- FillParams ---------------------------------------------------------------


@given(
    x=st.integers(min_value=-10000, max_value=10000),
    y=st.integers(min_value=-10000, max_value=10000),
    radius=st.integers(min_value=1, max_value=5000),
)
@settings(max_examples=50)
def test_fill_valid_inputs(x: int, y: int, radius: int) -> None:
    params = FillParams(x=x, y=y, radius=radius)
    assert params.radius == radius


# -- DrawShapeParams ----------------------------------------------------------


@given(
    shape=st.sampled_from(["rectangle", "ellipse", "line"]),
    x=st.integers(min_value=-10000, max_value=10000),
    y=st.integers(min_value=-10000, max_value=10000),
    width=st.integers(min_value=1, max_value=10000),
    height=st.integers(min_value=1, max_value=10000),
    fill=st.booleans(),
    stroke=st.booleans(),
)
@settings(max_examples=50)
def test_draw_shape_valid_inputs(shape: str, x: int, y: int, width: int, height: int, fill: bool, stroke: bool) -> None:
    params = DrawShapeParams(shape=shape, x=x, y=y, width=width, height=height, fill=fill, stroke=stroke)
    assert params.shape == shape


# -- SaveParams ---------------------------------------------------------------


@given(path=safe_path)
@settings(max_examples=50)
def test_save_valid_inputs(path: str) -> None:
    params = SaveParams(path=path)
    assert ".." not in params.path


# -- ClearParams --------------------------------------------------------------


@given(color=hex_color)
@settings(max_examples=50)
def test_clear_valid_inputs(color: str) -> None:
    params = ClearParams(color=color)
    assert params.color == color


# -- GetColorAtParams ---------------------------------------------------------


@given(
    x=st.integers(min_value=0, max_value=10000),
    y=st.integers(min_value=0, max_value=10000),
)
@settings(max_examples=50)
def test_get_color_at_valid_inputs(x: int, y: int) -> None:
    params = GetColorAtParams(x=x, y=y)
    assert params.x == x


# -- ListBrushesParams --------------------------------------------------------


@given(
    filter_str=st.text(max_size=50),
    limit=st.integers(min_value=1, max_value=500),
)
@settings(max_examples=50)
def test_list_brushes_valid_inputs(filter_str: str, limit: int) -> None:
    params = ListBrushesParams(filter=filter_str, limit=limit)
    assert params.limit == limit


# -- OpenFileParams -----------------------------------------------------------


@given(path=safe_path)
@settings(max_examples=50)
def test_open_file_valid_inputs(path: str) -> None:
    params = OpenFileParams(path=path)
    assert ".." not in params.path


# -- SetBrushParams -----------------------------------------------------------


@given(
    preset=st.text(max_size=50) | st.none(),
    size=st.integers(min_value=1, max_value=5000) | st.none(),
    opacity=st.floats(min_value=0.0, max_value=1.0) | st.none(),
)
@settings(max_examples=50)
def test_set_brush_valid_inputs(preset: str | None, size: int | None, opacity: float | None) -> None:
    params = SetBrushParams(preset=preset, size=size, opacity=opacity)
    assert params.preset == preset
