# Implementation Plan: Implement Batch Operations Endpoint

## Phase 1: Core Client & Pydantic Models
- [x] Task: Define Pydantic models for Batch Request
    - [x] Write Tests: Unit tests for batch model validation
    - [x] Implement Feature: Create `BatchRequest` and `BatchResponse` models in `src/krita_client/models.py`
- [x] Task: Add HTTP handler for batch
    - [x] Write Tests: Integration test using `pytest-httpx` for batch endpoint
    - [x] Implement Feature: Add `batch_execute` method in `src/krita_client/client.py`

## Phase 2: CLI & MCP Support
- [x] Task: Add CLI subcommand for batch
    - [x] Write Tests: Unit tests for parsing JSON into batch commands
    - [x] Implement Feature: Add `krita batch` subcommand in `src/krita_cli/cli.py`
- [x] Task: Add MCP tool for batch
    - [x] Write Tests: Unit tests for the FastMCP tool registration
    - [x] Implement Feature: Add `krita_batch` tool in `src/krita_mcp/server.py`

## Phase 3: Krita Plugin Integration
- [x] Task: Add action handler in the plugin
    - [x] Write Tests: E2E tests executing a batch of paint strokes
    - [x] Implement Feature: Update `krita-plugin/kritamcp/__init__.py` to process the `batch` action type over the command queue sequentially

