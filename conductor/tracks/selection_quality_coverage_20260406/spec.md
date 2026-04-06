# Track Specification: Selection Code Quality & Test Coverage

## Phase 11b: Selection Tools — Review Fixes

### Problem Statement

The Selection Tools track review identified 5 Medium/Low issues that need addressing: fragile API usage, inconsistent import patterns, missing property-based tests, missing MCP error-path tests, and a confusing CLI compatibility alias.

### Requirements

1. **Fix `cmd_select_ellipse` API robustness** — Wrap `selectEllipse` call in try/except with fallback to rectangular select for older Krita versions that lack the method.
2. **Fix `cmd_selection_info` bounds extraction** — Replace fragile `getattr(bounds, "x", lambda: 0)()` with direct method calls `bounds.x()`, etc., with proper error handling.
3. **Move PyQt5 imports to top level** — Move `QPolygon, QPoint` imports from inside `cmd_select_polygon` to the file's top-level PyQt5.QtCore import.
4. **Add property-based tests** — Use `hypothesis` to test selection model edge cases: arbitrary valid point lists, boundary dimensions, etc.
5. **Add MCP error-path tests** — Test error handling for selection MCP tools (KritaError paths).
6. **Clean up CLI alias** — Add deprecation note to `select-area` command or remove it.

### Acceptance Criteria

- [ ] `cmd_select_ellipse` has fallback for older Krita versions
- [ ] `cmd_selection_info` uses direct method calls with proper error handling
- [ ] All PyQt5 imports at top level in plugin `__init__.py`
- [ ] Property-based tests exist for selection models
- [ ] MCP error-path tests exist for selection tools
- [ ] CLI `select-area` alias has deprecation note (or removed)
- [ ] All new code passes lint, type check, and test suites
