# Track Specification: Selection Clipping Integration

## Phase 11b: Selection Tools — Missing Requirements

### Problem Statement

The Selection Tools spec explicitly requires: "When a selection is active, stroke/fill/draw commands are clipped to the selection boundary." This was not implemented. Additionally, several related gaps exist:

1. **No clipping verification** — Drawing commands (stroke, fill, draw_shape) do not verify that Krita's native clipping is active. The numpy-accelerated rendering path may bypass it entirely.
2. **No E2E tests** — Selection is inherently a Krita-runtime-dependent feature, but no E2E tests exist to verify selection behavior end-to-end.
3. **Silent clipping** — When drawing with an active selection, the MCP tool and CLI return success without mentioning that output was clipped. This can confuse users (especially AI agents) who don't realize their stroke was partially discarded.
4. **Undo/redo gap** — Selection operations may not integrate with Krita's undo stack, meaning users cannot revert selections via Ctrl+Z.
5. **No API version detection** — Krita versions may differ in Selection API availability (`selectEllipse`, `selectPolygon`, `bounds()`). Without version detection, these calls can fail silently or crash.

### Requirements

1. **Verify Native Clipping** — Confirm that Krita's native paint operations respect the active document selection mask. If they do, document and test. If not, implement mask-based clipping in plugin handlers.
2. **E2E Clipping Test** — Create the E2E test skeleton: create a selection, perform a draw operation outside the selection bounds, and verify no pixels were modified outside the selection.
3. **Clipping Awareness in Responses** — When a selection is active, MCP tools and CLI should indicate that drawing operations will be clipped. Include selection bounds in the response.
4. **Krita API Version Detection** — Detect the Krita API version at plugin startup. Gate selection features that depend on specific APIs (`selectEllipse`, `selectPolygon`, `bounds()`). Return `"supported": false` with guidance for missing APIs.
5. **Undo/redo for Selection** — Verify whether Krita's selection operations integrate with the undo stack. If not, implement undo support via Krita's `startTransaction`/`endTransaction` API.

### Acceptance Criteria

- [ ] Krita native clipping behavior verified and documented
- [ ] Numpy rendering path respects selection mask (or confirmed that Krita handles it)
- [ ] E2E test proves drawing outside selection has no effect
- [ ] MCP/CLI responses indicate active selection when drawing
- [ ] Krita API version detected at startup; unsupported features reported gracefully
- [ ] Selection operations support undo/redo
- [ ] All new code passes lint, type check, and test suites
