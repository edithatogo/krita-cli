# Track Specification: Selection Clipping Integration

## Phase 11b: Selection Tools — Missing Requirement

### Problem Statement

The Selection Tools spec requires: "When a selection is active, stroke/fill/draw commands are clipped to the selection boundary." This requirement was not implemented in the original track. Currently, selection commands create a Krita selection mask, but drawing commands (stroke, fill, draw_shape) do not verify that Krita's native clipping is active, and the numpy-accelerated rendering path may bypass it entirely.

### Requirements

1. **Verify Native Clipping** — Confirm that Krita's native paint operations (stroke, fill, shape drawing) respect the active document selection mask. If they do, document and test this behavior.
2. **Numpy Path Clipping** — If the `_draw_stroke_numpy` rendering path bypasses the selection mask, modify it to apply the selection mask as a clipping region.
3. **E2E Clipping Test** — Add an E2E test that creates a selection, performs a draw operation outside the selection bounds, and verifies no pixels were modified outside the selection.
4. **Client Awareness** — Optionally, the client can query `selection_info()` before drawing and warn the user that operations will be clipped.

### Acceptance Criteria

- [ ] Krita native clipping behavior verified and documented
- [ ] Numpy rendering path respects selection mask (or confirmed that Krita handles it)
- [ ] E2E test proves drawing outside selection has no effect
- [ ] All new code passes lint, type check, and test suites
