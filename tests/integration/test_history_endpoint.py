"""Integration tests for command history endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from krita_client import KritaClient
from krita_client.config import ClientConfig

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_get_command_history_success(httpx_mock: HTTPXMock) -> None:
    """Client can retrieve command history from the plugin."""
    httpx_mock.add_response(
        json={
            "status": "ok",
            "history": [
                {
                    "action": "set_color",
                    "params": {"color": "#ff0000"},
                    "timestamp": 1234567890.0,
                    "status": "ok",
                    "duration_ms": 15.5,
                },
                {
                    "action": "stroke",
                    "params": {"points": [[0, 0], [100, 100]]},
                    "timestamp": 1234567891.0,
                    "status": "ok",
                    "duration_ms": 25.0,
                },
            ],
            "count": 2,
        }
    )

    config = ClientConfig()
    with KritaClient(config) as client:
        result = client.get_command_history(limit=10)

    assert result["status"] == "ok"
    assert result["count"] == 2
    assert result["history"][0]["action"] == "set_color"
    assert result["history"][1]["action"] == "stroke"


def test_get_command_history_empty(httpx_mock: HTTPXMock) -> None:
    """Client handles empty history response."""
    httpx_mock.add_response(
        json={"status": "ok", "history": [], "count": 0}
    )

    config = ClientConfig()
    with KritaClient(config) as client:
        result = client.get_command_history()

    assert result["status"] == "ok"
    assert result["count"] == 0
    assert result["history"] == []
