# Implementation Plan: Selection Clipping Integration

## Phase 1: Investigate & Verify Native Clipping
- [ ] Task: Verify Krita native clipping behavior
    - [ ] Write Tests: E2E test creating a selection, drawing outside it, and verifying no pixels changed outside bounds
    - [ ] Implement Feature: Document findings; if native clipping works, add confirming test; if not, implement mask-based clipping in plugin handlers

## Phase 2: Numpy Path Clipping (if needed)
- [ ] Task: Apply selection mask to numpy rendering path
    - [ ] Write Tests: Unit tests for numpy stroke rendering with selection mask
    - [ ] Implement Feature: Modify `_draw_stroke_numpy` to accept and apply selection mask, or rely on Krita's native clipping
