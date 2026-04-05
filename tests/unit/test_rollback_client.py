"""Unit tests for KritaClient rollback method."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from krita_client.client import KritaClient, KritaCommandError


def test_client_rollback_success() -> None:
    client = KritaClient()
    mock_response = {"status": "ok"}

    with patch.object(client, "_send", return_value=mock_response) as mock_send:
        result = client.rollback(batch_id="test-id")

        mock_send.assert_called_once_with("rollback", {"batch_id": "test-id"})
        assert result["status"] == "ok"


def test_client_rollback_not_found() -> None:
    client = KritaClient()
    mock_error = {
        "error": {
            "code": "BATCH_NOT_FOUND",
            "message": "Batch not found",
            "recoverable": False,
        }
    }

    # KritaClient._send handles the 'error' key and raises KritaCommandError
    with patch.object(client._client, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_error
        mock_post.return_value = mock_resp

        with pytest.raises(KritaCommandError) as excinfo:
            client.rollback(batch_id="invalid-id")

        assert excinfo.value.code == "BATCH_NOT_FOUND"


def test_client_rollback_not_possible() -> None:
    client = KritaClient()
    mock_error = {
        "error": {
            "code": "ROLLBACK_NOT_POSSIBLE",
            "message": "Canvas has changed",
            "recoverable": False,
        }
    }

    with patch.object(client._client, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_error
        mock_post.return_value = mock_resp

        with pytest.raises(KritaCommandError) as excinfo:
            client.rollback(batch_id="test-id")

        assert excinfo.value.code == "ROLLBACK_NOT_POSSIBLE"
