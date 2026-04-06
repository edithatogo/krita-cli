# Track Specification: Selection Code Quality & Test Coverage

## Phase 11b: Selection Tools — Review Fixes

### Problem Statement

The Selection Tools track review identified 6 Medium/Low issues that need addressing:

1. **Duplicated boilerplate in plugin handlers** — Every selection handler repeats the pattern: `get_active_document()` → null check → `doc.selection()` → null check → `make_error()`. A shared `_get_selection_or_error()` helper would cut ~40 lines of boilerplate and reduce bug surface.
2. **Fragile `cmd_selection_info` bounds extraction** — Uses `getattr(bounds, "x", lambda: 0)()` which is fragile. Krita's `Selection.bounds()` returns a QRect-like object where `x`, `y`, `width`, `height` are callable methods. If the API changes, this silently returns zeros.
3. **Inline PyQt5 imports** — `from PyQt5.QtCore import QPolygon, QPoint` inside `cmd_select_polygon` duplicates the top-level `PyQt5.QtCore` import. Inconsistent and unnecessary overhead.
4. **No property-based tests** — The codebase uses `hypothesis` for property-based testing but selection models have none. Good candidates: arbitrary valid rectangles within canvas bounds, N-gon point lists with coordinates in [0, 8192], fuzzing that `SelectPolygonParams` rejects any list with <3 points or !=2 coords.
5. **No MCP error-path tests** — Only success paths are tested for the 8 new MCP selection tools.
6. **Confusing CLI alias** — `select-area` calls `select-rect` but the duplicate command may confuse users.

### Requirements

1. **Extract shared selection helper** — Create `_get_selection_or_error()` in the plugin that returns either `(selection, error_response)` tuple, consolidating the common null-check pattern.
2. **Fix `cmd_select_ellipse` API robustness** — Wrap `selectEllipse` in try/except with fallback to rectangular select for older Krita versions.
3. **Fix `cmd_selection_info` bounds extraction** — Replace fragile getattr chain with direct method calls and proper error handling.
4. **Consolidate PyQt5 imports** — Move `QPolygon, QPoint` to the top-level import with existing PyQt5.QtCore imports.
5. **Add property-based tests** — Use `hypothesis` in `tests/property/test_selection.py` for selection model edge cases.
6. **Add MCP error-path tests** — Add KritaError-path tests for selection MCP tools.
7. **Clean up CLI alias** — Add deprecation note to `select-area` help text.

### Acceptance Criteria

- [ ] `_get_selection_or_error()` helper eliminates duplicated null-check patterns
- [ ] `cmd_select_ellipse` has fallback for older Krita versions
- [ ] `cmd_selection_info` uses direct method calls with proper error handling
- [ ] All PyQt5 imports at top level in plugin `__init__.py`
- [ ] Property-based tests exist for selection models (hypothesis)
- [ ] MCP error-path tests exist for all 8 selection tools
- [ ] CLI `select-area` alias has deprecation note
- [ ] All new code passes lint, type check, and test suites
