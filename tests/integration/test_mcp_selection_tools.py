"""Integration tests for MCP selection tools."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_mcp import server


@pytest.fixture
def mock_client():
    with patch("krita_mcp.server._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_krita_select_rect(mock_client) -> None:
    mock_client.select_rect.return_value = {"status": "ok"}
    result = server.krita_select_rect(x=0, y=0, width=100, height=100)
    assert "Selected rectangle" in result
    mock_client.select_rect.assert_called_once_with(x=0, y=0, width=100, height=100)


def test_krita_select_ellipse(mock_client) -> None:
    mock_client.select_ellipse.return_value = {"status": "ok"}
    result = server.krita_select_ellipse(cx=50, cy=50, rx=20, ry=20)
    assert "Selected ellipse" in result
    mock_client.select_ellipse.assert_called_once_with(cx=50, cy=50, rx=20, ry=20)


def test_krita_select_polygon(mock_client) -> None:
    mock_client.select_polygon.return_value = {"status": "ok"}
    result = server.krita_select_polygon(points=[[0, 0], [10, 0], [0, 10]])
    assert "Selected polygon" in result
    mock_client.select_polygon.assert_called_once_with(points=[[0, 0], [10, 0], [0, 10]])


def test_krita_selection_info(mock_client) -> None:
    mock_client.selection_info.return_value = {
        "has_selection": True,
        "bounds": {"x": 10, "y": 10, "width": 5, "height": 5},
    }
    result = server.krita_selection_info()
    assert "Selection: x=10" in result


def test_krita_clear_selection(mock_client) -> None:
    mock_client.clear_selection.return_value = {"status": "ok"}
    result = server.krita_clear_selection()
    assert "Cleared selection" in result


def test_krita_invert_selection(mock_client) -> None:
    mock_client.invert_selection.return_value = {"status": "ok"}
    result = server.krita_invert_selection()
    assert "Inverted selection" in result


def test_krita_fill_selection(mock_client) -> None:
    mock_client.fill_selection.return_value = {"status": "ok"}
    result = server.krita_fill_selection()
    assert "Filled selection" in result


def test_krita_deselect(mock_client) -> None:
    mock_client.deselect.return_value = {"status": "ok"}
    result = server.krita_deselect()
    assert "Deselected" in result


def test_krita_select_by_color(mock_client) -> None:
    mock_client.select_by_color.return_value = {"status": "ok", "selected_count": 50}
    result = server.krita_select_by_color(x=10, y=10, tolerance=0.1, contiguous=True)
    assert "Magic wand" in result
    assert "50 pixels" in result


def test_krita_select_by_alpha(mock_client) -> None:
    mock_client.select_by_alpha.return_value = {"status": "ok", "selected_count": 30}
    result = server.krita_select_by_alpha(min_alpha=1, max_alpha=255)
    assert "Alpha selection" in result
    assert "30 pixels" in result


def test_krita_transform_selection(mock_client) -> None:
    mock_client.transform_selection.return_value = {"status": "ok"}
    result = server.krita_transform_selection(dx=10)
    assert "Transformed selection" in result


def test_krita_grow_selection(mock_client) -> None:
    mock_client.grow_selection.return_value = {"status": "ok"}
    result = server.krita_grow_selection(pixels=5)
    assert "Grew selection by 5px" in result


def test_krita_shrink_selection(mock_client) -> None:
    mock_client.shrink_selection.return_value = {"status": "ok"}
    result = server.krita_shrink_selection(pixels=5)
    assert "Shrunk selection by 5px" in result


def test_krita_border_selection(mock_client) -> None:
    mock_client.border_selection.return_value = {"status": "ok"}
    result = server.krita_border_selection(pixels=2)
    assert "Created 2px border" in result


def test_krita_save_selection(mock_client) -> None:
    mock_client.save_selection.return_value = {"status": "ok"}
    result = server.krita_save_selection(path="mask.png")
    assert "Saved selection to mask.png" in result


def test_krita_load_selection(mock_client) -> None:
    mock_client.load_selection.return_value = {"status": "ok"}
    result = server.krita_load_selection(path="mask.png")
    assert "Loaded selection from mask.png" in result


def test_krita_selection_stats(mock_client) -> None:
    mock_client.selection_stats.return_value = {
        "status": "ok",
        "pixel_count": 100,
        "bounding_box": {"width": 10, "height": 10},
    }
    result = server.krita_selection_stats()
    assert "Pixel count: 100" in result


def test_krita_save_selection_channel(mock_client) -> None:
    mock_client.save_selection_channel.return_value = {"status": "ok"}
    result = server.krita_save_selection_channel(name="ch1")
    assert "Saved selection channel 'ch1'" in result


def test_krita_load_selection_channel(mock_client) -> None:
    mock_client.load_selection_channel.return_value = {"status": "ok"}
    result = server.krita_load_selection_channel(name="ch1")
    assert "Loaded selection channel 'ch1'" in result


def test_krita_list_selection_channels(mock_client) -> None:
    mock_client.list_selection_channels.return_value = {"status": "ok", "count": 1, "channels": [{"name": "ch1"}]}
    result = server.krita_list_selection_channels()
    assert "Selection channels (1): ch1" in result
