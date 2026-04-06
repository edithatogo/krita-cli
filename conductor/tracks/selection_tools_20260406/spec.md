# Track Specification: Selection Tools

## Phase 11b: Selection Tools

### Problem Statement

Users (AI agents and developers) need to restrict drawing operations to specific regions of the canvas. Currently, all tools operate on the full canvas with no way to limit stroke, fill, or shape operations to a bounded area.

### Requirements

1. **Rectangular Selection** — Define a rectangular selection area; all subsequent drawing commands respect the selection bounds.
2. **Elliptical Selection** — Define an elliptical/circular selection area.
3. **Freehand/Polygon Selection** — Define an arbitrary polygon selection for irregular shapes.
4. **Selection State API** — Query current selection bounds, clear selection, check if selection is active.
5. **Inverted Selection** — Invert the current selection (select everything outside the current selection).
6. **Selection + Drawing Integration** — When a selection is active, stroke/fill/draw commands are clipped to the selection boundary.
7. **CLI Commands** — `krita select rect`, `krita select ellipse`, `krita select polygon`, `krita select clear`, `krita select info`, `krita select invert`.
8. **MCP Tools** — `krita_select_rect`, `krita_select_ellipse`, `krita_select_polygon`, `krita_select_clear`, `krita_select_info`, `krita_select_invert`.

### Acceptance Criteria

- [ ] Rectangular selection works and clips drawing operations
- [ ] Elliptical selection works and clips drawing operations
- [ ] Polygon selection works with arbitrary point lists
- [ ] Selection state can be queried and cleared
- [ ] Inverted selection works correctly
- [ ] Drawing outside selection boundary has no effect
- [ ] All new code passes lint, type check, and test suites
- [ ] Unit, integration, and property-based tests added
- [ ] CLI subcommands documented and functional
- [ ] MCP tools registered and discoverable
