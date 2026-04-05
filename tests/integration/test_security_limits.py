"""Integration tests for rate limiting and batch size enforcement."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from krita_client import KritaClient
from krita_client.config import ClientConfig

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_rate_limit_error_response(httpx_mock: HTTPXMock) -> None:
    """Client handles rate limit error response from plugin."""
    httpx_mock.add_response(
        json={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Max 60 commands per minute.",
                "recoverable": True,
            }
        },
        status_code=429,
    )

    config = ClientConfig()
    with KritaClient(config) as client:
        with pytest.raises(Exception) as exc_info:
            client.undo()

        assert "RATE_LIMIT_EXCEEDED" in str(exc_info.value) or "Rate limit" in str(exc_info.value)


def test_batch_size_exceeded_error(httpx_mock: HTTPXMock) -> None:
    """Client handles batch size exceeded error response."""
    httpx_mock.add_response(
        json={
            "error": {
                "code": "BATCH_SIZE_EXCEEDED",
                "message": "Batch size exceeds maximum of 50 commands.",
                "recoverable": True,
            }
        },
        status_code=400,
    )

    config = ClientConfig()
    with KritaClient(config) as client:
        with pytest.raises(Exception) as exc_info:
            client.batch_execute([{"action": "undo"} for _ in range(51)])

        assert "BATCH_SIZE_EXCEEDED" in str(exc_info.value) or "Batch size" in str(exc_info.value)


def test_layer_limit_exceeded_error(httpx_mock: HTTPXMock) -> None:
    """Client handles layer limit exceeded error response."""
    httpx_mock.add_response(
        json={
            "error": {
                "code": "LAYER_LIMIT_EXCEEDED",
                "message": "Maximum layer count exceeded (100)",
                "recoverable": True,
            }
        },
        status_code=500,
    )

    config = ClientConfig()
    with KritaClient(config) as client:
        with pytest.raises(Exception) as exc_info:
            client.create_layer(name="Too Many Layers")

        assert "LAYER_LIMIT_EXCEEDED" in str(exc_info.value) or "layer count" in str(exc_info.value)
