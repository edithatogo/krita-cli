# Implementation Plan: Selection Tools

## Phase 1: Core Client & Pydantic Models
- [ ] Task: Define Pydantic models for Selection
    - [ ] Write Tests: Unit tests for selection model validation (rect, ellipse, polygon)
    - [ ] Implement Feature: Create `SelectionRect`, `SelectionEllipse`, `SelectionPolygon`, `SelectionInfo` models in `src/krita_client/models.py`
- [ ] Task: Add HTTP handlers for selection operations
    - [ ] Write Tests: Integration tests using `pytest-httpx` for all selection endpoints
    - [ ] Implement Feature: Add selection methods in `src/krita_client/client.py` (select_rect, select_ellipse, select_polygon, select_clear, select_info, select_invert)

## Phase 2: Krita Plugin Integration
- [ ] Task: Add selection action handlers in the plugin
    - [ ] Write Tests: E2E tests creating selections and verifying clip behavior
    - [ ] Implement Feature: Update `krita-plugin/kritamcp/__init__.py` to handle selection actions using Krita's Selection API
    - [ ] Implement Feature: Clip drawing operations when selection is active (modify stroke/fill/shape handlers to respect selection mask)

## Phase 3: CLI & MCP Support
- [ ] Task: Add CLI subcommands for selection
    - [ ] Write Tests: Unit tests for CLI argument parsing and command dispatch
    - [ ] Implement Feature: Add `krita select` command group with subcommands (rect, ellipse, polygon, clear, info, invert) in `src/krita_cli/cli.py`
- [ ] Task: Add MCP tools for selection
    - [ ] Write Tests: Unit tests for FastMCP tool registration and input validation
    - [ ] Implement Feature: Register `krita_select_*` tools in `src/krita_mcp/server.py`
