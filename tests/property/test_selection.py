"""Property-based tests for selection pydantic models using hypothesis."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from krita_client.models import (
    SelectEllipseParams,
    SelectPolygonParams,
    SelectRectParams,
)


class TestSelectRectParamsProperty:
    """Property-based tests for rectangular selection model."""

    @given(
        x=st.integers(min_value=-10000, max_value=10000),
        y=st.integers(min_value=-10000, max_value=10000),
        width=st.integers(min_value=1, max_value=8192),
        height=st.integers(min_value=1, max_value=8192),
    )
    @settings(max_examples=100)
    def test_any_valid_rect_within_bounds(self, x: int, y: int, width: int, height: int) -> None:
        """Any coordinates within valid dimension ranges should create successfully."""
        params = SelectRectParams(x=x, y=y, width=width, height=height)
        assert params.width >= 1
        assert params.height >= 1

    @given(
        width=st.integers(min_value=8193, max_value=100000),
        height=st.integers(min_value=1, max_value=8192),
    )
    @settings(max_examples=50)
    def test_width_exceeding_max_rejected(self, width: int, height: int) -> None:
        """Width exceeding max canvas dimension should always be rejected."""
        with pytest.raises(ValidationError):
            SelectRectParams(x=0, y=0, width=width, height=height)

    @given(
        width=st.integers(min_value=1, max_value=8192),
        height=st.integers(min_value=8193, max_value=100000),
    )
    @settings(max_examples=50)
    def test_height_exceeding_max_rejected(self, width: int, height: int) -> None:
        """Height exceeding max canvas dimension should always be rejected."""
        with pytest.raises(ValidationError):
            SelectRectParams(x=0, y=0, width=width, height=height)


class TestSelectEllipseParamsProperty:
    """Property-based tests for elliptical selection model."""

    @given(
        cx=st.integers(min_value=-10000, max_value=10000),
        cy=st.integers(min_value=-10000, max_value=10000),
        rx=st.integers(min_value=1, max_value=8192),
        ry=st.integers(min_value=1, max_value=8192),
    )
    @settings(max_examples=100)
    def test_any_valid_ellipse_within_bounds(self, cx: int, cy: int, rx: int, ry: int) -> None:
        """Any center coordinates with valid radii should create successfully."""
        params = SelectEllipseParams(cx=cx, cy=cy, rx=rx, ry=ry)
        assert params.rx >= 1
        assert params.ry >= 1

    @given(rx=st.integers(min_value=0, max_value=0))
    @settings(max_examples=10)
    def test_zero_rx_always_rejected(self, rx: int) -> None:
        """Zero rx should always be rejected."""
        with pytest.raises(ValidationError):
            SelectEllipseParams(cx=0, cy=0, rx=rx, ry=50)


class TestSelectPolygonParamsProperty:
    """Property-based tests for polygon selection model."""

    @given(
        n_points=st.integers(min_value=3, max_value=100),
        coords=st.lists(
            st.tuples(
                st.integers(min_value=-10000, max_value=10000),
                st.integers(min_value=-10000, max_value=10000),
            ),
            min_size=3,
            max_size=100,
        ),
    )
    @settings(max_examples=100)
    def test_any_valid_polygon_with_3plus_points(self, n_points: int, coords: list[tuple[int, int]]) -> None:
        """Any polygon with 3+ valid 2D points should create successfully."""
        points = [list(c) for c in coords[:n_points]]
        params = SelectPolygonParams(points=points)
        assert len(params.points) >= 3

    @given(
        bad_points=st.lists(
            st.lists(st.integers(), min_size=1, max_size=5),
            min_size=3,
            max_size=10,
        ).filter(lambda pts: any(len(p) != 2 for p in pts)),
    )
    @settings(max_examples=50)
    def test_invalid_point_dimensions_rejected(self, bad_points: list[list[int]]) -> None:
        """Points with !=2 coordinates should always be rejected."""
        with pytest.raises(ValidationError):
            SelectPolygonParams(points=bad_points)
