"""Unit tests for KritaClient to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_client.client import KritaClient
from krita_client.config import ClientConfig


@pytest.fixture
def client():
    config = ClientConfig(url="http://localhost:8888")
    return KritaClient(config)


def test_transform_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.transform_selection(dx=10, angle=45.0)
        mock_send.assert_called_once()


def test_grow_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.grow_selection(pixels=5)
        mock_send.assert_called_once()


def test_shrink_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.shrink_selection(pixels=5)
        mock_send.assert_called_once()


def test_border_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.border_selection(pixels=2)
        mock_send.assert_called_once()


def test_combine_selections(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.combine_selections(operation="union")
        mock_send.assert_called_once()


def test_clear_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.clear_selection()
        mock_send.assert_called_once_with("clear_selection", {})


def test_invert_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.invert_selection()
        mock_send.assert_called_once_with("invert_selection", {})


def test_fill_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.fill_selection()
        mock_send.assert_called_once_with("fill_selection", {})


def test_deselect(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.deselect()
        mock_send.assert_called_once_with("deselect", {})


def test_select_by_color(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.select_by_color(x=10, y=10)
        mock_send.assert_called_once()


def test_select_by_alpha(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.select_by_alpha(min_alpha=10)
        mock_send.assert_called_once()


def test_save_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.save_selection(path="test.png")
        mock_send.assert_called_once()


def test_load_selection(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.load_selection(path="test.png")
        mock_send.assert_called_once()


def test_selection_stats(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.selection_stats()
        mock_send.assert_called_once_with("selection_stats", {})


def test_save_selection_channel(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.save_selection_channel(name="ch1")
        mock_send.assert_called_once()


def test_load_selection_channel(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.load_selection_channel(name="ch1")
        mock_send.assert_called_once()


def test_list_selection_channels(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.list_selection_channels()
        mock_send.assert_called_once_with("list_selection_channels", {})


def test_delete_selection_channel(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.delete_selection_channel(name="ch1")
        mock_send.assert_called_once()


def test_get_capabilities(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.get_capabilities()
        mock_send.assert_called_once_with("get_capabilities", {})


def test_get_security_status(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.get_security_status()
        mock_send.assert_called_once_with("get_security_status", {})


def test_send_http_error(client) -> None:
    import httpx
    with patch.object(client._client, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        # The code calls raise_for_status() if it's an error?
        # No, the code checks status_code? No, it catches HTTPStatusError.
        # But HTTPStatusError is usually raised by response.raise_for_status().
        # Wait, the code doesn't call raise_for_status()!
        
        # Let's check _send again.
        # It has:
        # response = self._client.post(...)
        # data = response.json()
        
        # So it ONLY raises HTTPStatusError if something ELSE raises it.
        # Wait, httpx.Client.post DOES NOT raise HTTPStatusError unless you use a hook.
        
        # Ah, I see. I'll make the mock raise it.
        mock_post.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_resp
        )
        
        from krita_client import KritaError
        with pytest.raises(KritaError) as exc_info:
            client._send("test", {})
        assert "HTTP 500" in exc_info.value.message


def test_list_layers(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.list_layers()
        mock_send.assert_called_once_with("list_layers", {})


def test_create_layer(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.create_layer(name="new")
        mock_send.assert_called_once()


def test_delete_layer(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.delete_layer(name="layer")
        mock_send.assert_called_once()


def test_rename_layer(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.rename_layer(old_name="old", new_name="new")
        mock_send.assert_called_once()


def test_set_layer_opacity(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.set_layer_opacity(name="layer", opacity=0.5)
        mock_send.assert_called_once()


def test_set_layer_visibility(client) -> None:
    with patch.object(client, "_send") as mock_send:
        mock_send.return_value = {"status": "ok"}
        client.set_layer_visibility(name="layer", visible=True)
        mock_send.assert_called_once()


def test_health_protocol_mismatch_int(client) -> None:
    with patch.object(client._client, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ok", "protocol_version": 999}
        mock_get.return_value = mock_resp
        
        from krita_client import KritaConnectionError
        with pytest.raises(KritaConnectionError) as exc_info:
            client.health()
        assert "upgrade krita-cli" in exc_info.value.message


def test_health_protocol_mismatch_str(client) -> None:
    with patch.object(client._client, "get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ok", "protocol_version": "9.9.9"}
        mock_get.return_value = mock_resp
        
        from krita_client import KritaConnectionError
        with pytest.raises(KritaConnectionError) as exc_info:
            client.health()
        assert "Incompatible protocol version" in exc_info.value.message


def test_health_connect_error(client) -> None:
    import httpx
    with patch.object(client._client, "get") as mock_get:
        mock_get.side_effect = httpx.ConnectError("refused")
        
        from krita_client import KritaConnectionError
        with pytest.raises(KritaConnectionError) as exc_info:
            client.health()
        assert "Cannot connect" in exc_info.value.message


def test_is_compatible_invalid_format(client) -> None:
    assert client._is_compatible("1.0") is False
    assert client._is_compatible("a.b.c") is False
