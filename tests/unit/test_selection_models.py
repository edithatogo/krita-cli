"""Unit tests for selection pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import (
    ClearSelectionParams,
    DeselectParams,
    FillSelectionParams,
    InvertSelectionParams,
    SelectEllipseParams,
    SelectionInfoParams,
    SelectPolygonParams,
    SelectRectParams,
)


class TestSelectRectParams:
    """Tests for rectangular selection model."""

    def test_valid_rect(self) -> None:
        """Valid rectangle selection should create successfully."""
        params = SelectRectParams(x=10, y=20, width=100, height=200)
        assert params.x == 10
        assert params.y == 20
        assert params.width == 100
        assert params.height == 200

    def test_zero_width_rejected(self) -> None:
        """Zero width should be rejected."""
        with pytest.raises(ValidationError):
            SelectRectParams(x=0, y=0, width=0, height=100)

    def test_negative_height_rejected(self) -> None:
        """Negative height should be rejected."""
        with pytest.raises(ValidationError):
            SelectRectParams(x=0, y=0, width=100, height=-1)

    def test_max_dimensions(self) -> None:
        """Max canvas dimensions should be accepted."""
        params = SelectRectParams(x=0, y=0, width=8192, height=8192)
        assert params.width == 8192
        assert params.height == 8192

    def test_exceed_max_dimensions_rejected(self) -> None:
        """Dimensions exceeding max should be rejected."""
        with pytest.raises(ValidationError):
            SelectRectParams(x=0, y=0, width=8193, height=8192)


class TestSelectEllipseParams:
    """Tests for elliptical selection model."""

    def test_valid_ellipse(self) -> None:
        """Valid ellipse selection should create successfully."""
        params = SelectEllipseParams(cx=100, cy=100, rx=50, ry=30)
        assert params.cx == 100
        assert params.cy == 100
        assert params.rx == 50
        assert params.ry == 30

    def test_zero_rx_rejected(self) -> None:
        """Zero rx should be rejected."""
        with pytest.raises(ValidationError):
            SelectEllipseParams(cx=0, cy=0, rx=0, ry=30)

    def test_negative_ry_rejected(self) -> None:
        """Negative ry should be rejected."""
        with pytest.raises(ValidationError):
            SelectEllipseParams(cx=0, cy=0, rx=50, ry=-1)

    def test_circle(self) -> None:
        """Circle selection (equal rx/ry) should work."""
        params = SelectEllipseParams(cx=50, cy=50, rx=25, ry=25)
        assert params.rx == params.ry


class TestSelectPolygonParams:
    """Tests for polygon selection model."""

    def test_valid_triangle(self) -> None:
        """Valid triangle polygon should create successfully."""
        params = SelectPolygonParams(points=[[0, 0], [100, 0], [50, 100]])
        assert len(params.points) == 3

    def test_valid_quad(self) -> None:
        """Valid quadrilateral should create successfully."""
        params = SelectPolygonParams(points=[[0, 0], [100, 0], [100, 100], [0, 100]])
        assert len(params.points) == 4

    def test_too_few_points_rejected(self) -> None:
        """Fewer than 3 points should be rejected."""
        with pytest.raises(ValidationError):
            SelectPolygonParams(points=[[0, 0], [100, 100]])

    def test_invalid_point_format_rejected(self) -> None:
        """Points with wrong coordinate count should be rejected."""
        with pytest.raises(ValidationError):
            SelectPolygonParams(points=[[0, 0, 0], [100, 100], [50, 50]])


class TestSelectionInfoParams:
    """Tests for selection info model."""

    def test_empty_params(self) -> None:
        """Selection info params should accept empty construction."""
        params = SelectionInfoParams()
        assert params is not None


class TestClearSelectionParams:
    """Tests for clear selection model."""

    def test_empty_params(self) -> None:
        """Clear selection params should accept empty construction."""
        params = ClearSelectionParams()
        assert params is not None


class TestInvertSelectionParams:
    """Tests for invert selection model."""

    def test_empty_params(self) -> None:
        """Invert selection params should accept empty construction."""
        params = InvertSelectionParams()
        assert params is not None


class TestFillSelectionParams:
    """Tests for fill selection model."""

    def test_empty_params(self) -> None:
        """Fill selection params should accept empty construction."""
        params = FillSelectionParams()
        assert params is not None


class TestDeselectParams:
    """Tests for deselect model."""

    def test_empty_params(self) -> None:
        """Deselect params should accept empty construction."""
        params = DeselectParams()
        assert params is not None
