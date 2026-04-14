# Implementation Plan: Selection Persistence & Session Management

## Phase 1: Core Models & Client
- [x] Task: Define Pydantic models for persistence operations
    - [x] Write Tests: Unit tests for SaveSelectionParams, LoadSelectionParams, SelectionChannelParams
    - [x] Implement Feature: Add models in `src/krita_client/models.py`
- [x] Task: Add HTTP handlers for save/load/stats operations
    - [x] Write Tests: Integration tests using `pytest-httpx`
    - [x] Implement Feature: Add client methods `save_selection`, `load_selection`, `selection_stats` in `src/krita_client/client.py`

## Phase 2: Krita Plugin Integration
- [x] Task: Implement selection export/import as PNG mask
    - [x] Write Tests: E2E tests saving selection to PNG and reloading, verifying pixel-level match
    - [x] Implement Feature: Render selection mask to QImage, save as PNG; load PNG, convert to selection mask
- [x] Task: Implement selection channels (named selections within document)
    - [x] Write Tests: E2E tests creating, listing, loading, and deleting channels
    - [x] Implement Feature: Store selection masks as document annotations
- [x] Task: Implement selection statistics calculation
    - [x] Write Tests: Unit tests for pixel counting, centroid calculation, area percentage
    - [x] Implement Feature: Scan selection mask, compute statistics

## Phase 3: CLI, MCP & Batch Integration
- [x] Task: Add CLI subcommands for persistence operations
    - [x] Write Tests: Unit tests for CLI argument parsing
    - [x] Implement Feature: Add `krita selection save`, `krita selection load`, `krita selection channels`, `krita selection stats`
- [x] Task: Add MCP tools for persistence operations
    - [x] Write Tests: Unit tests for FastMCP tool registration
    - [x] Implement Feature: Register `krita_save_selection`, `krita_load_selection`, `krita_list_selection_channels`, `krita_selection_stats`, `krita_save_selection_channel`, `krita_load_selection_channel`, `krita_list_selection_channels`, `krita_delete_selection_channel`
- [x] Task: Document and test batch operations with selection clipping
    - [x] Implement Feature: Document clipping behavior in product.md
