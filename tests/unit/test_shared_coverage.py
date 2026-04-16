"""Unit tests for _shared.py to improve coverage."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import typer

from krita_cli import _shared
from krita_client import KritaError, ErrorCode


def test_handle_error_hints() -> None:
    # Test each recoverable error code to cover hint lines
    error_codes = [
        ErrorCode.NO_ACTIVE_DOCUMENT,
        ErrorCode.INVALID_PARAMETERS,
        ErrorCode.LAYER_NOT_FOUND,
        ErrorCode.PLUGIN_UNREACHABLE,
        ErrorCode.COMMAND_TIMEOUT,
        ErrorCode.BRUSH_NOT_FOUND,
        ErrorCode.FILE_NOT_FOUND,
        "UNKNOWN_RECOVERABLE"
    ]
    
    for code in error_codes:
        exc = KritaError("message", code=code)
        exc.recoverable = True
        with pytest.raises(typer.Exit):
            _shared._handle_error(exc)


def test_handle_errors_context_manager() -> None:
    with pytest.raises(typer.Exit):
        with _shared._handle_errors():
            raise KritaError("fail")


def test_format_result_error() -> None:
    with pytest.raises(typer.Exit):
        _shared._format_result({"error": "failed"})


def test_print_result(capsys) -> None:
    _shared._print_result({"status": "ok", "foo": "bar"}, "SuccessMsg")
    captured = capsys.readouterr()
    assert "SuccessMsg" in captured.out
    assert "foo" in captured.out
    assert "bar" in captured.out
