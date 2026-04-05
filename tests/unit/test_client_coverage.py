"""Additional client tests for coverage of internal methods."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from krita_client.client import KritaClient, KritaValidationError
from krita_client.config import ClientConfig
from krita_client.models import NewCanvasParams


def test_validate_invalid_params() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    with pytest.raises(KritaValidationError):
        client._validate(NewCanvasParams, {"width": -1})


def test_send_with_timeout() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    client._client = MagicMock()
    client._client.post.return_value = mock_response
    result = client._send("test_action", timeout=60.0)
    assert result["status"] == "ok"
    call_kwargs = client._client.post.call_args[1]
    assert call_kwargs["timeout"].read == 60.0


def test_send_no_params() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    client._client = MagicMock()
    client._client.post.return_value = mock_response
    result = client._send("test_action")
    assert result["status"] == "ok"


def test_stroke_with_size() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    client._client = MagicMock()
    client._client.post.return_value = mock_response
    result = client.stroke(points=[[0, 0], [100, 100]], size=30)
    assert result["status"] == "ok"


def test_draw_shape_with_all_options() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    client._client = MagicMock()
    client._client.post.return_value = mock_response
    result = client.draw_shape(shape="line", x=0, y=0, x2=100, y2=100, fill=False, stroke=True)
    assert result["status"] == "ok"


def test_set_brush_with_all_options() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    client._client = MagicMock()
    client._client.post.return_value = mock_response
    result = client.set_brush(preset="Soft", size=50, opacity=0.8)
    assert result["status"] == "ok"
