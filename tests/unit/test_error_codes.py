"""Unit tests for ErrorCode enum and structured error handling."""

from __future__ import annotations

import pytest

from krita_client.client import (
    KritaCommandError,
    KritaConnectionError,
    KritaError,
    KritaValidationError,
)
from krita_client.models import ErrorCode

# -- ErrorCode enum tests -----------------------------------------------------


def test_error_code_values() -> None:
    expected = {
        "NO_ACTIVE_DOCUMENT",
        "NO_ACTIVE_LAYER",
        "NO_ACTIVE_VIEW",
        "INVALID_COLOR",
        "CANVAS_TOO_LARGE",
        "PATH_TRAVERSAL_BLOCKED",
        "FILE_NOT_FOUND",
        "PLUGIN_UNREACHABLE",
        "COMMAND_TIMEOUT",
        "INVALID_SHAPE",
        "LAYER_NOT_FOUND",
        "BRUSH_NOT_FOUND",
        "INVALID_PARAMETERS",
        "UNKNOWN_ACTION",
        "INTERNAL_ERROR",
        "INCOMPATIBLE_PROTOCOL",
        "RATE_LIMIT_EXCEEDED",
        "BATCH_SIZE_EXCEEDED",
        "LAYER_LIMIT_EXCEEDED",
        "ROLLBACK_NOT_POSSIBLE",
        "BATCH_NOT_FOUND",
        "PAYLOAD_TOO_LARGE",
    }
    assert {e.value for e in ErrorCode} == expected


def test_error_code_is_string_enum() -> None:
    assert ErrorCode.NO_ACTIVE_DOCUMENT == "NO_ACTIVE_DOCUMENT"
    assert ErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"


def test_error_code_membership() -> None:
    assert "NO_ACTIVE_DOCUMENT" in {e.value for e in ErrorCode}


# -- KritaError structured fields ---------------------------------------------


def test_krita_error_defaults() -> None:
    err = KritaError("something broke")
    assert err.message == "something broke"
    assert err.code is None
    assert err.recoverable is False


def test_krita_error_with_code() -> None:
    err = KritaError("no document", code=ErrorCode.NO_ACTIVE_DOCUMENT)
    assert err.code == ErrorCode.NO_ACTIVE_DOCUMENT


def test_krita_error_recoverable() -> None:
    err = KritaError("timeout", code=ErrorCode.COMMAND_TIMEOUT, recoverable=True)
    assert err.recoverable is True


def test_krita_error_is_exception() -> None:
    err = KritaError("boom")
    assert isinstance(err, Exception)
    assert str(err) == "boom"


def test_krita_connection_error_defaults() -> None:
    err = KritaConnectionError("cannot connect")
    assert err.message == "cannot connect"
    assert err.recoverable is False


def test_krita_command_error_defaults() -> None:
    err = KritaCommandError("command failed")
    assert err.message == "command failed"
    assert err.code is None


def test_krita_validation_error_defaults() -> None:
    err = KritaValidationError("bad params")
    assert err.message == "bad params"
    assert err.code is None


# -- Client error code assignments --------------------------------------------


def test_connection_error_has_plugin_unreachable_code() -> None:
    err = KritaConnectionError("cannot connect", code=ErrorCode.PLUGIN_UNREACHABLE, recoverable=True)
    assert err.code == ErrorCode.PLUGIN_UNREACHABLE
    assert err.recoverable is True


def test_command_error_with_internal_code() -> None:
    err = KritaCommandError("HTTP 500", code=ErrorCode.INTERNAL_ERROR)
    assert err.code == ErrorCode.INTERNAL_ERROR


def test_command_error_with_timeout_code() -> None:
    err = KritaCommandError("read timeout", code=ErrorCode.COMMAND_TIMEOUT, recoverable=True)
    assert err.code == ErrorCode.COMMAND_TIMEOUT
    assert err.recoverable is True


# -- Error code coverage for all enum values ----------------------------------


@pytest.mark.parametrize(
    "code",
    [
        ErrorCode.NO_ACTIVE_DOCUMENT,
        ErrorCode.NO_ACTIVE_LAYER,
        ErrorCode.NO_ACTIVE_VIEW,
        ErrorCode.INVALID_COLOR,
        ErrorCode.CANVAS_TOO_LARGE,
        ErrorCode.PATH_TRAVERSAL_BLOCKED,
        ErrorCode.FILE_NOT_FOUND,
        ErrorCode.PLUGIN_UNREACHABLE,
        ErrorCode.COMMAND_TIMEOUT,
        ErrorCode.INVALID_SHAPE,
        ErrorCode.LAYER_NOT_FOUND,
        ErrorCode.BRUSH_NOT_FOUND,
        ErrorCode.INVALID_PARAMETERS,
        ErrorCode.UNKNOWN_ACTION,
        ErrorCode.INTERNAL_ERROR,
        ErrorCode.INCOMPATIBLE_PROTOCOL,
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorCode.BATCH_SIZE_EXCEEDED,
        ErrorCode.LAYER_LIMIT_EXCEEDED,
        ErrorCode.ROLLBACK_NOT_POSSIBLE,
        ErrorCode.BATCH_NOT_FOUND,
    ],
)
def test_all_error_codes_usable_in_krita_error(code: ErrorCode) -> None:
    err = KritaError(f"test {code.value}", code=code, recoverable=True)
    assert err.code == code
    assert err.recoverable is True
