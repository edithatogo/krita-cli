"""Unit tests for krita_client.config."""

from __future__ import annotations

import os
from unittest.mock import patch

from krita_client.config import ClientConfig


def test_default_config() -> None:
    config = ClientConfig()
    assert config.url == "http://localhost:5678"
    assert config.port == 5678
    assert config.default_timeout == 30.0
    assert config.health_timeout == 5.0
    assert config.export_timeout == 120.0
    assert config.max_canvas_width == 8192
    assert config.max_canvas_height == 8192
    assert config.canvas_output_dir == "~/krita-mcp-output"


def test_env_var_override() -> None:
    with patch.dict(os.environ, {"KRITA_URL": "http://custom:9999", "KRITA_PORT": "9999"}):
        config = ClientConfig()
        assert config.url == "http://custom:9999"
        assert config.port == 9999


def test_custom_config() -> None:
    config = ClientConfig(url="http://test:1234", port=1234, default_timeout=60.0)
    assert config.url == "http://test:1234"
    assert config.port == 1234
    assert config.default_timeout == 60.0
