# Implementation Plan: Selection Advanced Features

## Phase 1: Core Models & Client
- [ ] Task: Define Pydantic models for color and alpha selection
    - [ ] Write Tests: Unit tests for SelectByColorParams, SelectByAlphaParams
    - [ ] Implement Feature: Add models in `src/krita_client/models.py`
- [ ] Task: Add HTTP handlers for color and alpha selection
    - [ ] Write Tests: Integration tests using `pytest-httpx`
    - [ ] Implement Feature: Add client methods `select_by_color`, `select_by_alpha` in `src/krita_client/client.py`

## Phase 2: Krita Plugin Integration
- [ ] Task: Add magic wand (color-based contiguous selection) handler
    - [ ] Write Tests: E2E tests selecting by color on test canvas with known pixel values
    - [ ] Implement Feature: Flood-fill algorithm using Krita's pixel API or custom implementation
- [ ] Task: Add global color selection handler
    - [ ] Write Tests: E2E tests selecting all matching pixels across canvas
    - [ ] Implement Feature: Scan all pixels, select those within color tolerance
- [ ] Task: Add alpha channel selection handler
    - [ ] Write Tests: E2E tests selecting by alpha range
    - [ ] Implement Feature: Scan alpha channel, create selection mask from alpha values

## Phase 3: CLI & MCP Support
- [ ] Task: Add CLI subcommands for color and alpha selection
    - [ ] Write Tests: Unit tests for CLI argument parsing
    - [ ] Implement Feature: Add `krita selection color` and `krita selection alpha` subcommands
- [ ] Task: Add MCP tools for color and alpha selection
    - [ ] Write Tests: Unit tests for FastMCP tool registration
    - [ ] Implement Feature: Register `krita_select_by_color` and `krita_select_by_alpha` in MCP server
