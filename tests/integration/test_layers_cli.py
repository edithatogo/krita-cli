"""Integration tests for layer CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from krita_cli.app import app
from krita_client import KritaError

runner = CliRunner()


@pytest.fixture
def mock_client():
    with patch("krita_cli._shared._get_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


def test_list_layers(mock_client) -> None:
    mock_client.list_layers.return_value = {
        "status": "ok",
        "layers": [{"name": "Background", "type": "paintlayer", "visible": True}],
        "count": 1,
    }
    result = runner.invoke(app, ["layers", "list"])
    assert result.exit_code == 0
    assert "Background" in result.stdout
    assert "paintlayer" in result.stdout


def test_create_layer(mock_client) -> None:
    mock_client.create_layer.return_value = {
        "status": "ok",
        "name": "New Layer",
        "type": "paintlayer",
    }
    result = runner.invoke(app, ["layers", "create", "--name", "New Layer"])
    assert result.exit_code == 0
    assert "New Layer" in result.stdout
    mock_client.create_layer.assert_called_once_with(name="New Layer", layer_type="paintlayer")


def test_select_layer(mock_client) -> None:
    mock_client.select_layer.return_value = {"status": "ok", "name": "Background"}
    result = runner.invoke(app, ["layers", "select", "Background"])
    assert result.exit_code == 0
    assert "Background" in result.stdout
    mock_client.select_layer.assert_called_once_with(name="Background")


def test_delete_layer(mock_client) -> None:
    mock_client.delete_layer.return_value = {"status": "ok", "name": "Layer 1"}
    result = runner.invoke(app, ["layers", "delete", "Layer 1"])
    assert result.exit_code == 0
    assert "Layer 1" in result.stdout
    mock_client.delete_layer.assert_called_once_with(name="Layer 1")


def test_rename_layer(mock_client) -> None:
    mock_client.rename_layer.return_value = {
        "status": "ok",
        "old_name": "Old",
        "new_name": "New",
    }
    result = runner.invoke(app, ["layers", "rename", "Old", "New"])
    assert result.exit_code == 0
    assert "Old" in result.stdout
    assert "New" in result.stdout
    mock_client.rename_layer.assert_called_once_with(old_name="Old", new_name="New")


def test_set_layer_opacity(mock_client) -> None:
    mock_client.set_layer_opacity.return_value = {
        "status": "ok",
        "name": "Layer 1",
        "opacity": 0.5,
    }
    result = runner.invoke(app, ["layers", "set-opacity", "Layer 1", "--opacity", "0.5"])
    assert result.exit_code == 0
    assert "Layer 1" in result.stdout
    assert "0.5" in result.stdout
    mock_client.set_layer_opacity.assert_called_once_with(name="Layer 1", opacity=0.5)


def test_set_layer_visibility(mock_client) -> None:
    mock_client.set_layer_visibility.return_value = {
        "status": "ok",
        "name": "Layer 1",
        "visible": False,
    }
    result = runner.invoke(app, ["layers", "set-visibility", "Layer 1", "--hidden"])
    assert result.exit_code == 0
    assert "Layer 1" in result.stdout
    assert "False" in result.stdout
    mock_client.set_layer_visibility.assert_called_once_with(name="Layer 1", visible=False)


def test_list_layers_error(mock_client) -> None:
    mock_client.list_layers.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "list"])
    assert result.exit_code == 1


def test_create_layer_error(mock_client) -> None:
    mock_client.create_layer.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "create", "--name", "New"])
    assert result.exit_code == 1


def test_select_layer_error(mock_client) -> None:
    mock_client.select_layer.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "select", "None"])
    assert result.exit_code == 1


def test_delete_layer_error(mock_client) -> None:
    mock_client.delete_layer.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "delete", "None"])
    assert result.exit_code == 1


def test_rename_layer_error(mock_client) -> None:
    mock_client.rename_layer.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "rename", "A", "B"])
    assert result.exit_code == 1


def test_set_layer_opacity_error(mock_client) -> None:
    mock_client.set_layer_opacity.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "set-opacity", "L", "--opacity", "0.5"])
    assert result.exit_code == 1


def test_set_layer_visibility_error(mock_client) -> None:
    mock_client.set_layer_visibility.side_effect = KritaError("failed")
    result = runner.invoke(app, ["layers", "set-visibility", "L", "--hidden"])
    assert result.exit_code == 1
