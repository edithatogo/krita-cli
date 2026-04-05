"""Unit tests for Batch operations models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import BatchCommand, BatchCommandResult, BatchRequest, BatchResponse


def test_batch_command_valid() -> None:
    cmd = BatchCommand(action="set_color", params={"color": "#ff0000"})
    assert cmd.action == "set_color"
    assert cmd.params == {"color": "#ff0000"}


def test_batch_request_valid() -> None:
    req = BatchRequest(
        commands=[
            BatchCommand(action="set_color", params={"color": "#ff0000"}),
            BatchCommand(action="stroke", params={"points": [[0, 0], [100, 100]]}),
        ]
    )
    assert len(req.commands) == 2


def test_batch_request_empty() -> None:
    with pytest.raises(ValidationError):
        BatchRequest(commands=[])


def test_batch_request_with_stop_on_error() -> None:
    req = BatchRequest(
        commands=[BatchCommand(action="undo")],
        stop_on_error=True
    )
    assert req.stop_on_error is True


def test_batch_command_result_ok() -> None:
    res = BatchCommandResult(action="set_color", status="ok", result={"status": "ok"})
    assert res.action == "set_color"
    assert res.status == "ok"
    assert res.result == {"status": "ok"}


def test_batch_command_result_error() -> None:
    res = BatchCommandResult(action="stroke", status="error", error="No active layer")
    assert res.action == "stroke"
    assert res.status == "error"
    assert res.error == "No active layer"


def test_batch_response_ok() -> None:
    res = BatchResponse(
        status="ok",
        results=[
            BatchCommandResult(action="set_color", status="ok", result={"status": "ok"}),
        ],
        count=1
    )
    assert res.status == "ok"
    assert len(res.results) == 1
    assert res.count == 1


def test_batch_response_partial() -> None:
    res = BatchResponse(
        status="partial",
        results=[
            BatchCommandResult(action="set_color", status="ok", result={"status": "ok"}),
            BatchCommandResult(action="stroke", status="error", error="No active layer"),
        ],
        count=2
    )
    assert res.status == "partial"
    assert len(res.results) == 2
