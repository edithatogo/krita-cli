"""Unit tests for payload size validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# Import payload_validator from plugin directory (not a pip package)
_payload_path = Path(__file__).parent.parent.parent / "krita-plugin" / "kritamcp" / "payload_validator.py"
_spec = importlib.util.spec_from_file_location("payload_validator", _payload_path)
_payload_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_payload_module)  # type: ignore[union-attr]

MAX_PAYLOAD_SIZE = _payload_module.MAX_PAYLOAD_SIZE
validate_payload_size = _payload_module.validate_payload_size


class TestValidatePayloadSize:
    """Tests for payload size validation."""

    def test_small_payload_passes(self) -> None:
        """Small payloads should pass validation."""
        assert validate_payload_size(1024) is None

    def test_max_payload_passes(self) -> None:
        """Payloads at the max limit should pass."""
        assert validate_payload_size(MAX_PAYLOAD_SIZE) is None

    def test_oversized_payload_rejected(self) -> None:
        """Payloads exceeding the limit should be rejected."""
        error = validate_payload_size(MAX_PAYLOAD_SIZE + 1)
        assert error is not None
        assert "Payload too large" in error

    def test_none_content_length_passes(self) -> None:
        """Missing Content-Length should pass (body will be checked after reading)."""
        assert validate_payload_size(None) is None

    def test_custom_max_size(self) -> None:
        """Custom max size should be respected."""
        assert validate_payload_size(500, max_size=1000) is None
        error = validate_payload_size(1001, max_size=1000)
        assert error is not None
        assert "1001" in error
