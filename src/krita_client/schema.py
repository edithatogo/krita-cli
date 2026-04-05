"""OpenAPI schema generation from pydantic models."""

from __future__ import annotations

from typing import Any

from krita_client.models import COMMAND_MODELS


def generate_openapi_schema(
    title: str = "Krita MCP Plugin API",
    version: str = "0.1.0",
    description: str = "HTTP API for the Krita MCP plugin. Send POST requests to / with JSON bodies.",
) -> dict[str, Any]:
    """Generate an OpenAPI 3.1 schema from the command pydantic models.

    This schema documents the HTTP API that the Krita plugin exposes,
    making it easy for third-party integrations to understand the
    available commands and their parameters.
    """
    paths: dict[str, Any] = {}
    schemas: dict[str, Any] = {}

    for action, model_cls in COMMAND_MODELS.items():
        schema = model_cls.model_json_schema()
        model_name = model_cls.__name__
        schemas[model_name] = schema

        paths[f"/commands/{action}"] = {
            "post": {
                "summary": f"Execute the {action} command",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "const": action},
                                    "params": {"$ref": f"#/components/schemas/{model_name}"},
                                },
                                "required": ["action"],
                            },
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Command executed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "500": {
                        "description": "Command execution failed",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }

    paths["/health"] = {
        "get": {
            "summary": "Health check",
            "responses": {
                "200": {
                    "description": "Plugin is running",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string"},
                                    "plugin": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": description,
        },
        "paths": paths,
        "components": {"schemas": schemas},
    }
