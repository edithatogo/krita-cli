# Implementation Plan: Selection Clipping Integration

## Phase 1: Investigate & Verify Native Clipping
- [ ] Task: Verify Krita native clipping behavior
    - [ ] Write Tests: E2E test creating a selection, drawing outside it, and verifying no pixels changed outside bounds
    - [ ] Implement Feature: Document findings; if native clipping works, add confirming test; if not, implement mask-based clipping in plugin handlers
- [ ] Task: Add clipping awareness to responses
    - [ ] Implement Feature: When selection is active, include "clipped_by_selection": true in stroke/fill/draw responses

## Phase 2: Krita API Version Detection
- [ ] Task: Detect Krita API version at startup
    - [ ] Write Tests: Unit tests for version detection and feature gating
    - [ ] Implement Feature: Add API version check in plugin init; gate selectEllipse, selectPolygon, bounds() behind availability checks
    - [ ] Implement Feature: Return "supported": false with guidance for unavailable APIs

## Phase 3: Undo/redo Integration
- [ ] Task: Verify and implement undo support for selection operations
    - [ ] Write Tests: E2E test that verifies undo restores selection state
    - [ ] Implement Feature: Wrap selection operations in Krita transaction API if needed
