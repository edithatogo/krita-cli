# Implementation Plan: Selection Tools

## Phase 1: Core Client & Pydantic Models
- [x] Task: Define Pydantic models for Selection
    - [x] Write Tests: Unit tests for selection model validation (rect, ellipse, polygon)
    - [x] Implement Feature: Create `SelectionRect`, `SelectionEllipse`, `SelectionPolygon`, `SelectionInfo` models in `src/krita_client/models.py`
- [x] Task: Add HTTP handlers for selection operations
    - [x] Write Tests: Integration tests using `pytest-httpx` for all selection endpoints
    - [x] Implement Feature: Add selection methods in `src/krita_client/client.py` (select_rect, select_ellipse, select_polygon, select_clear, select_info, select_invert)

## Phase 2: Krita Plugin Integration
- [x] Task: Add selection action handlers in the plugin
    - [x] Write Tests: E2E tests creating selections and verifying clip behavior
    - [x] Implement Feature: Update `krita-plugin/kritamcp/__init__.py` to handle selection actions using Krita's Selection API
    - [x] Implement Feature: Clip drawing operations when selection is active (modify stroke/fill/shape handlers to respect selection mask)

## Phase 3: CLI & MCP Support
- [x] Task: Add CLI subcommands for selection
    - [x] Write Tests: Unit tests for CLI argument parsing and command dispatch
    - [x] Implement Feature: Add `krita select` command group with subcommands (rect, ellipse, polygon, clear, info, invert) in `src/krita_cli/cli.py`
- [x] Task: Add MCP tools for selection
    - [x] Write Tests: Unit tests for FastMCP tool registration and input validation
    - [x] Implement Feature: Register `krita_select_*` tools in `src/krita_mcp/server.py`
