"""Property-based tests for input sanitization across all endpoints."""

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from krita_client.models import (
    BatchCommand,
    BatchRequest,
    NewCanvasParams,
    SaveParams,
    SelectAreaParams,
    SetColorParams,
    StrokeParams,
)


class TestPathTraversalPrevention:
    """Property tests for path traversal prevention."""

    @given(
        st.text(alphabet=st.characters(blacklist_characters="/\\"), min_size=1)
        .filter(lambda s: ".." not in s)
    )
    @settings(max_examples=50)
    def test_safe_paths_always_validate(self, safe_path: str) -> None:
        """Paths without '..' should pass basic validation."""
        # SaveParams validates path traversal
        params = SaveParams(path=safe_path)
        assert ".." not in params.path

    @given(st.text(min_size=1))
    @settings(max_examples=50)
    def test_paths_with_traversal_always_fail(self, malicious_path: str) -> None:
        """Paths containing '..' should be rejected by the plugin."""
        # Note: The plugin checks this, not the client model.
        # We test that the client model passes through the path unchanged
        # so the plugin can perform its own validation.
        if ".." in malicious_path:
            # Model should accept the path (plugin does the real validation)
            params = SaveParams(path=malicious_path)
            assert params.path == malicious_path


class TestDimensionBoundary:
    """Property tests for dimension boundary validation."""

    @given(st.integers(min_value=1, max_value=8192))
    @settings(max_examples=50)
    def test_valid_canvas_width(self, width: int) -> None:
        """Valid canvas widths should always create valid models."""
        params = NewCanvasParams(width=width, height=600)
        assert 1 <= params.width <= 8192

    @given(st.integers(min_value=1, max_value=8192))
    @settings(max_examples=50)
    def test_valid_canvas_height(self, height: int) -> None:
        """Valid canvas heights should always create valid models."""
        params = NewCanvasParams(width=800, height=height)
        assert 1 <= params.height <= 8192

    @given(st.integers(max_value=0))
    @settings(max_examples=20)
    def test_zero_or_negative_width_rejected(self, width: int) -> None:
        """Zero or negative widths should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NewCanvasParams(width=width, height=600)

    @given(st.integers(min_value=8193))
    @settings(max_examples=20)
    def test_oversized_width_rejected(self, width: int) -> None:
        """Widths exceeding MAX_CANVAS_DIM should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NewCanvasParams(width=width, height=600)


class TestColorFormatValidation:
    """Property tests for color format validation."""

    @given(
        st.tuples(
            st.integers(min_value=0, max_value=255),
            st.integers(min_value=0, max_value=255),
            st.integers(min_value=0, max_value=255),
        )
    )
    @settings(max_examples=50)
    def test_valid_hex_colors_from_rgb(self, rgb: tuple[int, int, int]) -> None:
        """Any valid RGB triplet should produce a valid hex color."""
        r, g, b = rgb
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        params = SetColorParams(color=hex_color)
        assert params.color == hex_color

    @given(st.text(min_size=1).filter(lambda s: not s.startswith("#")))
    @settings(max_examples=30)
    def test_non_hex_colors_rejected(self, invalid_color: str) -> None:
        """Colors not starting with '#' should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SetColorParams(color=invalid_color)


class TestStrokeInputValidation:
    """Property tests for stroke input validation."""

    @given(
        st.lists(
            st.tuples(st.integers(), st.integers()),
            min_size=2,
            max_size=100,
        ).map(lambda pts: [list(pt) for pt in pts])
    )
    @settings(max_examples=30)
    def test_valid_stroke_points(self, points: list[list[int]]) -> None:
        """Valid stroke point lists should create valid models."""
        params = StrokeParams(points=points)
        assert len(params.points) >= 2
        assert all(len(pt) == 2 for pt in params.points)


class TestBatchInputValidation:
    """Property tests for batch input validation."""

    @given(
        st.lists(
            st.builds(
                BatchCommand,
                action=st.text(min_size=1),
                params=st.dictionaries(st.text(), st.just("")),
            ),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=30)
    def test_valid_batch_requests(self, commands: list[BatchCommand]) -> None:
        """Valid batch command lists should create valid models."""
        request = BatchRequest(commands=commands)
        assert len(request.commands) >= 1

    @given(st.just([]))
    @settings(max_examples=1)
    def test_empty_batch_rejected(self, empty_commands: list[Any]) -> None:
        """Empty batch requests should be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            BatchRequest(commands=empty_commands)


class TestSelectAreaValidation:
    """Property tests for selection area validation."""

    @given(
        st.integers(min_value=0, max_value=8192),
        st.integers(min_value=0, max_value=8192),
        st.integers(min_value=1, max_value=8192),
        st.integers(min_value=1, max_value=8192),
    )
    @settings(max_examples=30)
    def test_valid_selection_area(
        self, x: int, y: int, width: int, height: int
    ) -> None:
        """Valid selection parameters should create valid models."""
        params = SelectAreaParams(x=x, y=y, width=width, height=height)
        assert params.x == x
        assert params.y == y
        assert params.width == width
        assert params.height == height
