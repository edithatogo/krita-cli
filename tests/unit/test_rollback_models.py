"""Unit tests for rollback-related models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from krita_client.models import (
    BatchResponse,
    RollbackParams,
    RollbackResponse,
)


def test_batch_response_with_id() -> None:
    resp = BatchResponse(
        status="ok",
        results=[],
        count=0,
        batch_id="550e8400-e29b-41d4-a716-446655440000"
    )
    assert resp.batch_id == "550e8400-e29b-41d4-a716-446655440000"


def test_batch_response_optional_id() -> None:
    resp = BatchResponse(status="ok", results=[], count=0)
    assert resp.batch_id is None


def test_rollback_params() -> None:
    params = RollbackParams(batch_id="test-id")
    assert params.batch_id == "test-id"


def test_rollback_params_invalid() -> None:
    with pytest.raises(ValidationError):
        RollbackParams()


def test_rollback_response_ok() -> None:
    resp = RollbackResponse(status="ok")
    assert resp.status == "ok"
    assert resp.message is None


def test_rollback_response_error() -> None:
    resp = RollbackResponse(status="error", message="Canvas changed")
    assert resp.status == "error"
    assert resp.message == "Canvas changed"
