"""Integration tests for MCP layer tools."""

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


def test_krita_list_layers(mock_client) -> None:
    mock_client.list_layers.return_value = {"status": "ok", "count": 2, "layers": [{"name": "Ink"}, {"name": "Color"}]}
    result = server.krita_list_layers()
    assert "Layers (2): Ink, Color" in result


def test_krita_create_layer(mock_client) -> None:
    mock_client.create_layer.return_value = {"status": "ok", "name": "Sketch", "type": "paintlayer"}
    result = server.krita_create_layer(name="Sketch")
    assert "Created layer 'Sketch' (paintlayer)" in result
    mock_client.create_layer.assert_called_once_with(name="Sketch", layer_type="paintlayer")


def test_krita_select_layer(mock_client) -> None:
    mock_client.select_layer.return_value = {"status": "ok", "selected": "Sketch"}
    result = server.krita_select_layer(name="Sketch")
    assert "Selected layer 'Sketch'" in result
    mock_client.select_layer.assert_called_once_with(name="Sketch")


def test_krita_delete_layer(mock_client) -> None:
    mock_client.delete_layer.return_value = {"status": "ok", "deleted": "Sketch"}
    result = server.krita_delete_layer(name="Sketch")
    assert "Deleted layer 'Sketch'" in result
    mock_client.delete_layer.assert_called_once_with(name="Sketch")


def test_krita_rename_layer(mock_client) -> None:
    mock_client.rename_layer.return_value = {"status": "ok"}
    result = server.krita_rename_layer(old_name="Sketch", new_name="Lineart")
    assert "Renamed layer 'Sketch' to 'Lineart'" in result
    mock_client.rename_layer.assert_called_once_with(old_name="Sketch", new_name="Lineart")


def test_krita_set_layer_opacity(mock_client) -> None:
    mock_client.set_layer_opacity.return_value = {"status": "ok"}
    result = server.krita_set_layer_opacity(name="Sketch", opacity=0.5)
    assert "Set layer 'Sketch' opacity to 0.5" in result
    mock_client.set_layer_opacity.assert_called_once_with(name="Sketch", opacity=0.5)


def test_krita_set_layer_visibility(mock_client) -> None:
    mock_client.set_layer_visibility.return_value = {"status": "ok"}
    result = server.krita_set_layer_visibility(name="Sketch", visible=False)
    assert "Set layer 'Sketch' to hidden" in result
    mock_client.set_layer_visibility.assert_called_once_with(name="Sketch", visible=False)
