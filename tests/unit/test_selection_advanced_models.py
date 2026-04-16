"""Unit tests for selection advanced features models (color & alpha)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import SelectByColorParams, SelectByAlphaParams


class TestSelectByColorParams:
    """Tests for SelectByColorParams model."""

    def test_magic_wand_defaults(self) -> None:
        """Magic wand selection with defaults."""
        params = SelectByColorParams(x=50, y=50)
        assert params.x == 50
        assert params.y == 50
        assert params.tolerance == 0.1
        assert params.contiguous is True

    def test_global_color_selection(self) -> None:
        """Global color selection (no point specified)."""
        params = SelectByColorParams(x=None, y=None, tolerance=0.2, contiguous=False)
        assert params.x is None
        assert params.y is None
        assert params.tolerance == 0.2
        assert params.contiguous is False

    def test_tolerance_range_valid(self) -> None:
        """Tolerance within valid range."""
        params1 = SelectByColorParams(tolerance=0.0)
        assert params1.tolerance == 0.0
        params2 = SelectByColorParams(tolerance=1.0)
        assert params2.tolerance == 1.0

    def test_tolerance_range_invalid(self) -> None:
        """Tolerance outside valid range should raise."""
        with pytest.raises(ValidationError):
            SelectByColorParams(tolerance=-0.1)
        with pytest.raises(ValidationError):
            SelectByColorParams(tolerance=1.5)


class TestSelectByAlphaParams:
    """Tests for SelectByAlphaParams model."""

    def test_defaults(self) -> None:
        """Default alpha range."""
        params = SelectByAlphaParams()
        assert params.min_alpha == 1
        assert params.max_alpha == 255

    def test_custom_range(self) -> None:
        """Custom alpha range."""
        params = SelectByAlphaParams(min_alpha=50, max_alpha=200)
        assert params.min_alpha == 50
        assert params.max_alpha == 200

    def test_alpha_range_valid(self) -> None:
        """Alpha values within valid range."""
        params1 = SelectByAlphaParams(min_alpha=0, max_alpha=255)
        assert params1.min_alpha == 0
        assert params1.max_alpha == 255

    def test_alpha_range_invalid(self) -> None:
        """Alpha values outside valid range should raise."""
        with pytest.raises(ValidationError):
            SelectByAlphaParams(min_alpha=-1)
        with pytest.raises(ValidationError):
            SelectByAlphaParams(max_alpha=256)
        with pytest.raises(ValidationError):
            SelectByAlphaParams(min_alpha=300)
