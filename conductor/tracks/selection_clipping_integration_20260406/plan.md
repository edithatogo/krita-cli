# Implementation Plan: Selection Clipping Integration

## Phase 1: Investigate & Verify Native Clipping [pending_commit]
- [x] Task: Verify Krita native clipping behavior
    - [x] Write Tests: E2E test creating a selection, drawing outside it, and verifying no pixels changed outside bounds
    - [x] Implement Feature: Document findings; if native clipping works, add confirming test; if not, implement mask-based clipping in plugin handlers
- [x] Task: Add clipping awareness to responses
    - [x] Implement Feature: When selection is active, include "clipped_by_selection": true in stroke/fill/draw responses

## Phase 2: Krita API Version Detection [pending_commit]
- [x] Task: Detect Krita API version at startup
    - [x] Write Tests: Unit tests for version detection and feature gating
    - [x] Implement Feature: Add API version check in plugin init; gate selectEllipse, selectPolygon, bounds() behind availability checks
    - [x] Implement Feature: Return "supported": false with guidance for unavailable APIs

## Phase 3: Undo/redo Integration [pending_commit]
- [x] Task: Verify and implement undo support for selection operations
    - [x] Write Tests: E2E test that verifies undo restores selection state
    - [x] Implement Feature: Wrap selection operations in Krita transaction API if needed
