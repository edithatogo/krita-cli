"""Integration tests for Batch execution in KritaClient."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from krita_client.client import KritaClient

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def test_batch_execute_success(httpx_mock: HTTPXMock) -> None:
    # Set up mock response
    expected_response = {
        "status": "ok",
        "results": [
            {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
            {"action": "stroke", "status": "ok", "result": {"status": "ok"}},
        ],
        "count": 2,
    }
    httpx_mock.add_response(method="POST", url="http://localhost:5678/", json=expected_response)

    client = KritaClient()
    commands = [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
    ]

    # We use batch_execute which we will implement next
    result = client.batch_execute(commands)

    assert result["status"] == "ok"
    assert len(result["results"]) == 2
    assert result["count"] == 2

    # Verify the sent body
    request = httpx_mock.get_request()
    body = json.loads(request.read())
    assert body["action"] == "batch"
    assert body["params"]["commands"][0]["action"] == "set_color"
    assert body["params"]["stop_on_error"] is False


def test_batch_execute_stop_on_error(httpx_mock: HTTPXMock) -> None:
    expected_response = {
        "status": "partial",
        "results": [
            {"action": "set_color", "status": "ok", "result": {"status": "ok"}},
            {"action": "stroke", "status": "error", "error": "No active layer"},
        ],
        "count": 2,
    }
    httpx_mock.add_response(method="POST", url="http://localhost:5678/", json=expected_response)

    client = KritaClient()
    commands = [
        {"action": "set_color", "params": {"color": "#ff0000"}},
        {"action": "stroke", "params": {"points": [[0, 0], [100, 100]]}},
    ]

    result = client.batch_execute(commands, stop_on_error=True)

    assert result["status"] == "partial"

    # Verify the sent body
    request = httpx_mock.get_request()
    body = json.loads(request.read())
    assert body["params"]["stop_on_error"] is True


def test_batch_execute_empty(httpx_mock: HTTPXMock) -> None:
    from krita_client.client import KritaValidationError

    client = KritaClient()
    with pytest.raises(KritaValidationError):
        client.batch_execute([])
