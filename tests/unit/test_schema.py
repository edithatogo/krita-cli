"""Unit tests for krita_client.schema."""

from __future__ import annotations

from krita_client.schema import generate_openapi_schema


def test_generate_openapi_schema() -> None:
    schema = generate_openapi_schema()
    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["title"] == "Krita MCP Plugin API"
    assert "paths" in schema
    assert "components" in schema
    assert "schemas" in schema["components"]


def test_schema_has_health_endpoint() -> None:
    schema = generate_openapi_schema()
    assert "/health" in schema["paths"]
    assert "get" in schema["paths"]["/health"]


def test_schema_has_command_paths() -> None:
    schema = generate_openapi_schema()
    # All commands should have paths
    command_paths = [p for p in schema["paths"] if p.startswith("/commands/")]
    assert len(command_paths) >= 15  # At least 15 commands


def test_schema_has_component_schemas() -> None:
    schema = generate_openapi_schema()
    schemas = schema["components"]["schemas"]
    assert "NewCanvasParams" in schemas
    assert "StrokeParams" in schemas
    assert "BatchRequest" in schemas


def test_custom_title_and_version() -> None:
    schema = generate_openapi_schema(title="Custom", version="2.0.0")
    assert schema["info"]["title"] == "Custom"
    assert schema["info"]["version"] == "2.0.0"
