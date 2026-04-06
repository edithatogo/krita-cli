"""Payload size validator for HTTP request bodies.

Prevents oversized requests from causing memory issues or DoS.
"""

from __future__ import annotations

MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB default


def validate_payload_size(content_length: int | None, max_size: int = MAX_PAYLOAD_SIZE) -> str | None:
    """Validate that the request payload is within size limits.

    Args:
        content_length: Content-Length header value, or None if not present.
        max_size: Maximum allowed payload size in bytes.

    Returns:
        Error message if payload is too large, None if OK.
    """
    if content_length is not None and content_length > max_size:
        return f"Payload too large: {content_length} bytes exceeds maximum of {max_size} bytes"
    return None
