# Implementation Plan: Selection Persistence & Session Management

## Phase 1: Core Models & Client [pending_commit]
- [x] Task: Define Pydantic models for persistence operations
    - [x] Write Tests: Unit tests for SaveSelectionParams, LoadSelectionParams, SelectionChannelParams
    - [x] Implement Feature: Add models in `src/krita_client/models.py`
- [x] Task: Add HTTP handlers for save/load/stats operations
    - [x] Write Tests: Integration tests using `pytest-httpx`
    - [x] Implement Feature: Add client methods `save_selection`, `load_selection`, `selection_stats` in `src/krita_client/client.py`

## Phase 2: Krita Plugin Integration [pending_commit]
- [x] Task: Implement selection export/import as PNG mask
    - [x] Write Tests: E2E tests saving selection to PNG and reloading, verifying pixel-level match
    - [x] Implement Feature: Render selection mask to QImage, save as PNG; load PNG, convert to selection mask
- [~] Task: Implement selection channels (named selections within document)
    - [ ] Write Tests: E2E tests creating, listing, loading, and deleting channels
    - [ ] Implement Feature: Store selection masks as document layers or metadata
- [x] Task: Implement selection statistics calculation
    - [x] Write Tests: Unit tests for pixel counting, centroid calculation, area percentage
    - [x] Implement Feature: Scan selection mask, compute statistics

## Phase 3: CLI, MCP & Batch Integration
- [~] Task: Add CLI subcommands for persistence operations
    - [ ] Write Tests: Unit tests for CLI argument parsing
    - [ ] Implement Feature: Add `krita selection save`, `krita selection load`, `krita selection channels`, `krita selection stats`
- [~] Task: Add MCP tools for persistence operations
    - [ ] Write Tests: Unit tests for FastMCP tool registration
    - [ ] Implement Feature: Register `krita_save_selection`, `krita_load_selection`, `krita_list_selection_channels`, `krita_selection_stats`
- [ ] Task: Document and test batch operations with selection clipping
    - [ ] Implement Feature: Add `respect_selection` flag to batch request model; document clipping behavior
