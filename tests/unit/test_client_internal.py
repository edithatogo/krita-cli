"""Tests for client internal methods to reach 100% coverage."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from krita_client.client import KritaClient, KritaConnectionError
from krita_client.config import ClientConfig


def test_health_get_connection_error() -> None:
    """Test _health_get raises KritaConnectionError on connect failure."""
    config = ClientConfig(url="http://localhost:5678")
    client = KritaClient(config)
    client._client = MagicMock()
    client._client.get.side_effect = httpx.ConnectError("refused")
    with pytest.raises(KritaConnectionError):
        client._health_get()
