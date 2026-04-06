# Implementation Plan: Selection Code Quality & Test Coverage

## Phase 1: Plugin Handler Refactoring
- [ ] Task: Extract `_get_selection_or_error()` shared helper
    - [ ] Write Tests: Unit tests for the helper (null doc, null selection, success paths)
    - [ ] Implement Feature: Create helper in plugin; refactor all selection handlers to use it
- [ ] Task: Fix `cmd_select_ellipse` API robustness
    - [ ] Write Tests: Test that older Krita without selectEllipse falls back gracefully
    - [ ] Implement Feature: Wrap `selectEllipse` in try/except, fallback to rectangular select
- [ ] Task: Fix `cmd_selection_info` bounds extraction
    - [ ] Write Tests: Test bounds extraction with mock Selection.bounds()
    - [ ] Implement Feature: Replace fragile getattr chain with direct method calls and error handling
- [ ] Task: Consolidate PyQt5 imports to top level
    - [ ] Implement Feature: Add `QPolygon, QPoint` to top-level PyQt5.QtCore import, remove inline import in `cmd_select_polygon`

## Phase 2: Test Coverage Expansion
- [ ] Task: Add property-based tests for selection models
    - [ ] Implement Feature: Create `tests/property/test_selection.py` with hypothesis-based tests:
        - Arbitrary valid rectangles within canvas bounds
        - N-gon point lists with coordinates in valid ranges
        - Fuzzing: reject <3 points or !=2 coords per point
        - Ellipse radii boundary values (0, 1, 8192, 8193)
- [ ] Task: Add MCP error-path tests for selection tools
    - [ ] Implement Feature: Add KritaError-path tests in `tests/integration/test_mcp_error_result.py` for all 8 selection MCP tools

## Phase 3: CLI Cleanup
- [ ] Task: Add deprecation note to `select-area` CLI alias
    - [ ] Implement Feature: Update help text to indicate "alias for select-rect, prefer select-rect"
