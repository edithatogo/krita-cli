"""Configuration for the Krita MCP client."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientConfig(BaseSettings):
    """Configuration for the Krita MCP client.

    All settings can be overridden via environment variables
    with the ``KRITA_`` prefix (e.g. ``KRITA_URL``, ``KRITA_PORT``).
    """

    model_config = SettingsConfigDict(
        env_prefix="KRITA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "http://localhost:5678"
    """Base URL of the Krita plugin HTTP server."""

    port: int = 5678
    """Port the Krita plugin listens on (used for URL construction if url is default)."""

    default_timeout: float = 30.0
    """Default timeout in seconds for most commands."""

    health_timeout: float = 5.0
    """Timeout in seconds for health checks."""

    export_timeout: float = 120.0
    """Timeout in seconds for canvas export and save operations."""

    max_canvas_width: int = 8192
    """Maximum allowed canvas width to prevent OOM."""

    max_canvas_height: int = 8192
    """Maximum allowed canvas height to prevent OOM."""

    canvas_output_dir: str = "~/krita-mcp-output"
    """Default directory for canvas exports."""

    max_commands_per_minute: int = 60
    """Maximum commands per minute before rate limiting kicks in."""

    max_batch_size: int = 50
    """Maximum number of commands allowed in a single batch request."""

    max_layers: int = 100
    """Maximum number of layers per document to prevent OOM."""
