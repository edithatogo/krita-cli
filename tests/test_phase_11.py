from unittest.mock import patch

import pytest

from krita_client.client import KritaClient
from krita_client.models import CreateLayerParams, InvertSelectionParams


@pytest.fixture
def client():
    return KritaClient()


def test_undo_redo(client):
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}

        client.undo()
        mock_send.assert_called_with("undo", {})

        client.redo()
        mock_send.assert_called_with("redo", {})


def test_invert_selection(client):
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}

        client.invert_selection()
        mock_send.assert_called_with("invert_selection", {})


def test_create_layer_params():
    params = CreateLayerParams(name="Test", layer_type="paintlayer")
    assert params.name == "Test"
    assert params.layer_type == "paintlayer"


def test_invert_selection_params():
    params = InvertSelectionParams()
    assert params == InvertSelectionParams()
