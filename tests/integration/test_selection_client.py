"""Integration tests for Selection operations in KritaClient."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from krita_client.client import KritaClient

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock


def _setup_mock(httpx_mock: HTTPXMock, action: str) -> None:
    httpx_mock.add_response(method="POST", url="http://localhost:5678/", json={"status": "ok", "action": action})


def test_select_rect(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "select_rect")
    client = KritaClient()
    result = client.select_rect(10, 20, width=100, height=200)

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "select_rect"
    assert body["params"]["x"] == 10
    assert body["params"]["y"] == 20
    assert body["params"]["width"] == 100
    assert body["params"]["height"] == 200


def test_select_ellipse(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "select_ellipse")
    client = KritaClient()
    result = client.select_ellipse(50, 50, rx=30, ry=20)

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "select_ellipse"
    assert body["params"]["cx"] == 50
    assert body["params"]["cy"] == 50
    assert body["params"]["rx"] == 30
    assert body["params"]["ry"] == 20


def test_select_polygon(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "select_polygon")
    client = KritaClient()
    points = [[0, 0], [100, 0], [50, 100]]
    result = client.select_polygon(points)

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "select_polygon"
    assert body["params"]["points"] == points


def test_selection_info(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "selection_info")
    client = KritaClient()
    result = client.selection_info()

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "selection_info"
    assert body["params"] == {}


def test_clear_selection(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "clear_selection")
    client = KritaClient()
    result = client.clear_selection()

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "clear_selection"


def test_invert_selection(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "invert_selection")
    client = KritaClient()
    result = client.invert_selection()

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "invert_selection"


def test_fill_selection(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "fill_selection")
    client = KritaClient()
    result = client.fill_selection()

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "fill_selection"


def test_deselect(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "deselect")
    client = KritaClient()
    result = client.deselect()

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "deselect"


def test_combine_selections(httpx_mock: HTTPXMock) -> None:
    _setup_mock(httpx_mock, "combine_selections")
    client = KritaClient()
    result = client.combine_selections("union", mask_path="mask.png")

    assert result["status"] == "ok"
    req = httpx_mock.get_request()
    body = json.loads(req.read())
    assert body["action"] == "combine_selections"
    assert body["params"]["operation"] == "union"
    assert body["params"]["mask_path"] == "mask.png"
