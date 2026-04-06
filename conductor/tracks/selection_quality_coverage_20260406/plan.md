# Implementation Plan: Selection Code Quality & Test Coverage

## Phase 1: Plugin Handler Fixes
- [ ] Task: Fix `cmd_select_ellipse` API robustness
    - [ ] Write Tests: Test that older Krita without selectEllipse falls back gracefully
    - [ ] Implement Feature: Wrap `selectEllipse` in try/except, fallback to rectangular select
- [ ] Task: Fix `cmd_selection_info` bounds extraction
    - [ ] Write Tests: Test bounds extraction with mock Selection.bounds()
    - [ ] Implement Feature: Replace fragile getattr chain with direct method calls and error handling
- [ ] Task: Move PyQt5 imports to top level
    - [ ] Implement Feature: Add `QPolygon, QPoint` to top-level PyQt5.QtCore import, remove inline import

## Phase 2: Test Coverage Expansion
- [ ] Task: Add property-based tests for selection models
    - [ ] Implement Feature: Create `tests/property/test_selection.py` with hypothesis-based tests for SelectRectParams, SelectEllipseParams, SelectPolygonParams
- [ ] Task: Add MCP error-path tests for selection tools
    - [ ] Implement Feature: Add error-path tests in `tests/integration/test_mcp_error_result.py` for selection MCP tools

## Phase 3: CLI Cleanup
- [ ] Task: Clean up `select-area` CLI alias
    - [ ] Implement Feature: Add deprecation note to `select-area` help text, or remove the alias entirely
