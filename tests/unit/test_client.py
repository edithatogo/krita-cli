"""Unit tests for krita_client.client."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from krita_client.client import (
    KritaClient,
    KritaCommandError,
    KritaConnectionError,
    KritaValidationError,
)
from krita_client.config import ClientConfig


@pytest.fixture
def mock_response() -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"status": "ok"}
    response.text = ""
    return response


@pytest.fixture
def mock_client(mock_response: MagicMock) -> KritaClient:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    client._client = MagicMock(spec=httpx.Client)
    client._client.post.return_value = mock_response
    client._client.get.return_value = mock_response
    return client


# -- Health -------------------------------------------------------------------


def test_health(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {"status": "ok", "plugin": "kritamcp"}
    result = mock_client.health()
    assert result["status"] == "ok"
    mock_client._client.get.assert_called_once()


def test_health_connection_error(mock_client: KritaClient) -> None:
    mock_client._client.get.side_effect = httpx.ConnectError("refused")
    with pytest.raises(KritaConnectionError):
        mock_client.health()


def test_health_with_protocol_version_string(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {
        "status": "ok",
        "plugin": "kritamcp",
        "protocol_version": "1.0.0",
    }
    result = mock_client.health()
    assert result["status"] == "ok"
    assert result["protocol_version"] == "1.0.0"


def test_health_with_protocol_version_int(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {
        "status": "ok",
        "plugin": "kritamcp",
        "protocol_version": 1,
    }
    result = mock_client.health()
    assert result["status"] == "ok"
    assert result["protocol_version"] == 1


def test_health_incompatible_protocol_version_string(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {
        "status": "ok",
        "plugin": "kritamcp",
        "protocol_version": "2.0.0",
    }
    with pytest.raises(KritaConnectionError) as exc_info:
        mock_client.health()
    assert exc_info.value.code == "INCOMPATIBLE_PROTOCOL"
    assert "2.0.0" in str(exc_info.value)


def test_health_incompatible_protocol_version_int(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {
        "status": "ok",
        "plugin": "kritamcp",
        "protocol_version": 99,
    }
    with pytest.raises(KritaConnectionError) as exc_info:
        mock_client.health()
    assert exc_info.value.code == "INCOMPATIBLE_PROTOCOL"


def test_health_no_protocol_version(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {"status": "ok", "plugin": "kritamcp"}
    result = mock_client.health()
    assert result["status"] == "ok"


# -- Canvas operations --------------------------------------------------------


def test_new_canvas(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_response.json.return_value = {"status": "ok", "width": 800, "height": 600}
    result = mock_client.new_canvas(width=800, height=600)
    assert result["width"] == 800
    mock_client._client.post.assert_called_once()


def test_new_canvas_validation() -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    client._client = MagicMock(spec=httpx.Client)
    with pytest.raises(KritaValidationError, match="greater than or equal to 1"):
        client.new_canvas(width=0)


def test_set_color(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.set_color(color="#ff0000")
    assert result["status"] == "ok"
    call_args = mock_client._client.post.call_args
    assert call_args[1]["json"]["params"]["color"] == "#ff0000"


def test_stroke(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.stroke(points=[[0, 0], [100, 100]])
    assert result["status"] == "ok"


def test_fill(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.fill(x=50, y=50, radius=30)
    assert result["status"] == "ok"


def test_undo(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.undo()
    assert result["status"] == "ok"


def test_redo(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.redo()
    assert result["status"] == "ok"


def test_clear(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.clear(color="#000000")
    assert result["status"] == "ok"


def test_save(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.save(path="/tmp/test.png")
    assert result["status"] == "ok"


def test_get_color_at(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.get_color_at(x=10, y=20)
    assert result["status"] == "ok"


def test_list_brushes(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.list_brushes(filter="soft", limit=5)
    assert result["status"] == "ok"


def test_open_file(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.open_file(path="/tmp/test.kra")
    assert result["status"] == "ok"


# -- Batch --------------------------------------------------------------------


def test_batch(mock_client: KritaClient, mock_response: MagicMock) -> None:
    commands = [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
    ]
    result = mock_client.batch(commands)
    assert result["status"] == "ok"


def test_batch_with_stop_on_error(mock_client: KritaClient, mock_response: MagicMock) -> None:
    commands = [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
    ]
    result = mock_client.batch(commands, stop_on_error=True)
    assert result["status"] == "ok"
    call_args = mock_client._client.post.call_args
    assert call_args[1]["json"]["params"]["stop_on_error"] is True


def test_batch_empty_commands(mock_client: KritaClient) -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    client._client = MagicMock(spec=httpx.Client)
    with pytest.raises(KritaValidationError):
        client.batch([])


# -- Generic command dispatch -------------------------------------------------


def test_send_command_known_action(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.send_command("set_color", {"color": "#ff0000"})
    assert result["status"] == "ok"


def test_send_command_unknown_action(mock_client: KritaClient, mock_response: MagicMock) -> None:
    result = mock_client.send_command("custom_action", {"foo": "bar"})
    assert result["status"] == "ok"
    call_args = mock_client._client.post.call_args
    assert call_args[1]["json"]["action"] == "custom_action"


# -- Error handling -----------------------------------------------------------


def test_http_status_error(mock_client: KritaClient) -> None:
    error_response = MagicMock(spec=httpx.Response)
    error_response.status_code = 500
    error_response.text = "Internal Server Error"
    mock_client._client.post.side_effect = httpx.HTTPStatusError("error", request=MagicMock(), response=error_response)
    with pytest.raises(KritaCommandError) as exc_info:
        mock_client.set_color(color="#ff0000")
    assert exc_info.value.code == "INTERNAL_ERROR"


def test_generic_http_error(mock_client: KritaClient) -> None:
    mock_client._client.post.side_effect = httpx.ReadTimeout("timeout")
    with pytest.raises(KritaCommandError):
        mock_client.set_color(color="#ff0000")


# -- Context manager ----------------------------------------------------------


def test_context_manager(mock_response: MagicMock) -> None:
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    client._client = MagicMock()
    client._client.get.return_value = mock_response
    with client:
        client.health()
    client._client.close.assert_called_once()


# -- Export timeout -----------------------------------------------------------


def test_get_canvas_uses_export_timeout(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_client.get_canvas(filename="test.png")
    call_args = mock_client._client.post.call_args
    timeout = call_args[1]["timeout"]
    assert timeout.read == 120.0


def test_save_uses_export_timeout(mock_client: KritaClient, mock_response: MagicMock) -> None:
    mock_client.save(path="/tmp/test.png")
    call_args = mock_client._client.post.call_args
    timeout = call_args[1]["timeout"]
    assert timeout.read == 120.0
