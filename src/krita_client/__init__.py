"""Krita MCP Client — Typed HTTP client for the Krita plugin.

This package provides:
- ``ClientConfig``: Configuration via pydantic-settings.
- ``KritaClient``: Typed HTTP client with validated commands.
- Pydantic models for all 14 command parameter sets.
- OpenAPI schema generation.
"""

from __future__ import annotations

from krita_client.client import (
    KritaClient,
    KritaCommandError,
    KritaConnectionError,
    KritaError,
    KritaValidationError,
)
from krita_client.config import ClientConfig
from krita_client.models import (
    COMMAND_MODELS,
    BatchCommand,
    BatchParams,
    ClearParams,
    DrawShapeParams,
    FillParams,
    GetCanvasParams,
    GetColorAtParams,
    ListBrushesParams,
    NewCanvasParams,
    OpenFileParams,
    RedoParams,
    SaveParams,
    SetBrushParams,
    SetColorParams,
    StrokeParams,
    UndoParams,
)
from krita_client.schema import generate_openapi_schema

__all__ = [
    "COMMAND_MODELS",
    "BatchCommand",
    "BatchParams",
    "ClearParams",
    "ClientConfig",
    "DrawShapeParams",
    "FillParams",
    "GetCanvasParams",
    "GetColorAtParams",
    "KritaClient",
    "KritaCommandError",
    "KritaConnectionError",
    "KritaError",
    "KritaValidationError",
    "ListBrushesParams",
    "NewCanvasParams",
    "OpenFileParams",
    "RedoParams",
    "SaveParams",
    "SetBrushParams",
    "SetColorParams",
    "StrokeParams",
    "UndoParams",
    "generate_openapi_schema",
]
