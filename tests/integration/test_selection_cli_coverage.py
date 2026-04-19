"""Integration tests for selection CLI commands to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app

runner = CliRunner()


@pytest.fixture
def mock_client():
    with patch("krita_cli._shared._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_select_rect(mock_client) -> None:
    mock_client.select_rect.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-rect", "10", "20", "100", "200"])
    assert result.exit_code == 0
    mock_client.select_rect.assert_called_once_with(x=10, y=20, width=100, height=200)


def test_select_ellipse(mock_client) -> None:
    mock_client.select_ellipse.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-ellipse", "50", "50", "30", "30"])
    assert result.exit_code == 0
    mock_client.select_ellipse.assert_called_once_with(cx=50, cy=50, rx=30, ry=30)


def test_select_polygon(mock_client) -> None:
    mock_client.select_polygon.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-polygon", "0,0", "100,0", "100,100"])
    assert result.exit_code == 0
    mock_client.select_polygon.assert_called_once_with(points=[[0, 0], [100, 0], [100, 100]])


def test_select_polygon_invalid_format(mock_client) -> None:
    result = runner.invoke(app, ["selection", "select-polygon", "0,0,0"])
    assert result.exit_code == 1
    assert "Invalid point format" in result.stdout


def test_select_polygon_invalid_coords(mock_client) -> None:
    result = runner.invoke(app, ["selection", "select-polygon", "a,b"])
    assert result.exit_code == 1
    assert "Invalid point coordinates" in result.stdout


def test_select_area_compat(mock_client) -> None:
    mock_client.select_rect.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-area", "10", "10", "50", "50"])
    assert result.exit_code == 0
    mock_client.select_rect.assert_called_once()


def test_clear_selection(mock_client) -> None:
    mock_client.clear_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-clear"])
    assert result.exit_code == 0


def test_invert_selection(mock_client) -> None:
    mock_client.invert_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-invert"])
    assert result.exit_code == 0


def test_fill_selection(mock_client) -> None:
    mock_client.fill_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "select-fill"])
    assert result.exit_code == 0


def test_selection_info(mock_client) -> None:
    mock_client.selection_info.return_value = {
        "status": "ok",
        "has_selection": True,
        "bounds": {"x": 0, "y": 0, "width": 100, "height": 100},
    }
    result = runner.invoke(app, ["selection", "select-info"])
    assert result.exit_code == 0
    assert "Active selection" in result.stdout


def test_selection_info_none(mock_client) -> None:
    mock_client.selection_info.return_value = {"status": "ok", "has_selection": False}
    result = runner.invoke(app, ["selection", "select-info"])
    assert result.exit_code == 0
    assert "No active selection" in result.stdout


def test_deselect(mock_client) -> None:
    mock_client.deselect.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "deselect"])
    assert result.exit_code == 0


def test_select_by_color(mock_client) -> None:
    mock_client.select_by_color.return_value = {"status": "ok", "selected_count": 100}
    result = runner.invoke(app, ["selection", "select-by-color", "-x", "50", "-y", "50", "-t", "0.2"])
    assert result.exit_code == 0
    assert "Magic wand" in result.stdout
    mock_client.select_by_color.assert_called_once_with(x=50, y=50, tolerance=0.2, contiguous=True)


def test_select_by_alpha(mock_client) -> None:
    mock_client.select_by_alpha.return_value = {"status": "ok", "selected_count": 200}
    result = runner.invoke(app, ["selection", "select-by-alpha", "--min", "10", "--max", "200"])
    assert result.exit_code == 0
    assert "Alpha selection" in result.stdout
    mock_client.select_by_alpha.assert_called_once_with(min_alpha=10, max_alpha=200)


def test_transform_selection(mock_client) -> None:
    mock_client.transform_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "transform-selection", "--dx", "10", "--angle", "45"])
    assert result.exit_code == 0
    mock_client.transform_selection.assert_called_once_with(dx=10, dy=0, angle=45.0, scale_x=1.0, scale_y=1.0)


def test_grow_selection(mock_client) -> None:
    mock_client.grow_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "grow-selection", "5"])
    assert result.exit_code == 0
    mock_client.grow_selection.assert_called_once_with(5)


def test_shrink_selection(mock_client) -> None:
    mock_client.shrink_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "shrink-selection", "5"])
    assert result.exit_code == 0
    mock_client.shrink_selection.assert_called_once_with(5)


def test_border_selection(mock_client) -> None:
    mock_client.border_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "border-selection", "2"])
    assert result.exit_code == 0
    mock_client.border_selection.assert_called_once_with(2)


def test_combine_selections(mock_client) -> None:
    mock_client.combine_selections.return_value = {"status": "ok", "selected_count": 42}
    result = runner.invoke(app, ["selection", "combine-selections", "union", "mask.png"])
    assert result.exit_code == 0
    assert "Combined selection via union" in result.stdout
    mock_client.combine_selections.assert_called_once_with(operation="union", mask_path="mask.png")


def test_save_selection(mock_client) -> None:
    mock_client.save_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "save-selection", "mask.png"])
    assert result.exit_code == 0
    mock_client.save_selection.assert_called_once_with(path="mask.png")


def test_load_selection(mock_client) -> None:
    mock_client.load_selection.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "load-selection", "mask.png"])
    assert result.exit_code == 0
    mock_client.load_selection.assert_called_once_with(path="mask.png")


def test_selection_stats(mock_client) -> None:
    mock_client.selection_stats.return_value = {
        "status": "ok",
        "pixel_count": 500,
        "bounding_box": {"x": 0, "y": 0, "width": 50, "height": 10},
        "centroid": {"x": 25, "y": 5},
        "area_percentage": 5.0,
    }
    result = runner.invoke(app, ["selection", "selection-stats"])
    assert result.exit_code == 0
    assert "Pixel count: 500" in result.stdout
    assert "Centroid: (25, 5)" in result.stdout


def test_save_channel(mock_client) -> None:
    mock_client.save_selection_channel.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "save-channel", "MySel"])
    assert result.exit_code == 0
    mock_client.save_selection_channel.assert_called_once_with(name="MySel")


def test_load_channel(mock_client) -> None:
    mock_client.load_selection_channel.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "load-channel", "MySel"])
    assert result.exit_code == 0
    mock_client.load_selection_channel.assert_called_once_with(name="MySel")


def test_list_channels(mock_client) -> None:
    mock_client.list_selection_channels.return_value = {
        "status": "ok",
        "channels": [{"name": "Ch1"}, {"name": "Ch2"}],
        "count": 2,
    }
    result = runner.invoke(app, ["selection", "list-channels"])
    assert result.exit_code == 0
    assert "Ch1" in result.stdout
    assert "Ch2" in result.stdout


def test_list_channels_empty(mock_client) -> None:
    mock_client.list_selection_channels.return_value = {"status": "ok", "channels": [], "count": 0}
    result = runner.invoke(app, ["selection", "list-channels"])
    assert result.exit_code == 0
    assert "No saved selection channels" in result.stdout


def test_delete_channel(mock_client) -> None:
    mock_client.delete_selection_channel.return_value = {"status": "ok"}
    result = runner.invoke(app, ["selection", "delete-channel", "Ch1"])
    assert result.exit_code == 0
    mock_client.delete_selection_channel.assert_called_once_with(name="Ch1")


def test_security_status(mock_client) -> None:
    mock_client.get_security_status.return_value = {
        "status": "ok",
        "rate_limit": {"current_usage": 5, "max_commands_per_minute": 60},
        "payload_limit": 10 * 1024 * 1024,
        "batch_size_limit": 100,
        "max_canvas_dim": 8192,
        "max_layers": 50,
    }
    result = runner.invoke(app, ["selection", "security-status"])
    assert result.exit_code == 0
    assert "Security Status" in result.stdout
    assert "5/60 per minute" in result.stdout
    assert "10MB" in result.stdout
