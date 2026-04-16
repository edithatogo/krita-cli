"""Unit tests for selection persistence models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import (
    SaveSelectionParams,
    LoadSelectionParams,
    SelectionChannelParams,
    SelectionStatsParams,
)


class TestSaveSelectionParams:
    """Tests for SaveSelectionParams model."""

    def test_defaults(self) -> None:
        """Default save params."""
        params = SaveSelectionParams(path="/tmp/selection.png")
        assert params.path == "/tmp/selection.png"
        assert params.format == "png"

    def test_custom_format(self) -> None:
        """Custom format."""
        params = SaveSelectionParams(path="/tmp/sel.bmp", format="bmp")
        assert params.format == "bmp"

    def test_empty_path_invalid(self) -> None:
        """Empty path should be invalid."""
        with pytest.raises(ValidationError):
            SaveSelectionParams(path="")


class TestLoadSelectionParams:
    """Tests for LoadSelectionParams model."""

    def test_valid_path(self) -> None:
        """Valid path."""
        params = LoadSelectionParams(path="/tmp/selection.png")
        assert params.path == "/tmp/selection.png"

    def test_empty_path_invalid(self) -> None:
        """Empty path should be invalid."""
        with pytest.raises(ValidationError):
            LoadSelectionParams(path="")


class TestSelectionChannelParams:
    """Tests for SelectionChannelParams model."""

    def test_valid_name(self) -> None:
        """Valid channel name."""
        params = SelectionChannelParams(name="my_channel")
        assert params.name == "my_channel"


class TestSelectionStatsParams:
    """Tests for SelectionStatsParams model."""

    def test_empty_params(self) -> None:
        """Stats params should be empty."""
        params = SelectionStatsParams()
        assert True  # Just verify it instantiates
