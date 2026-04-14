# Implementation Plan: Selection Advanced Features

## Phase 1: Core Models & Client [pending_commit]
- [x] Task: Define Pydantic models for color and alpha selection
    - [x] Write Tests: Unit tests for SelectByColorParams, SelectByAlphaParams
    - [x] Implement Feature: Add models in `src/krita_client/models.py`
- [x] Task: Add HTTP handlers for color and alpha selection
    - [x] Write Tests: Integration tests using `pytest-httpx`
    - [x] Implement Feature: Add client methods `select_by_color`, `select_by_alpha` in `src/krita_client/client.py`

## Phase 2: Krita Plugin Integration [pending_commit]
- [x] Task: Add magic wand (color-based contiguous selection) handler
    - [x] Write Tests: E2E tests selecting by color on test canvas with known pixel values
    - [x] Implement Feature: Flood-fill algorithm using Krita's pixel API or custom implementation
- [x] Task: Add global color selection handler
    - [x] Write Tests: E2E tests selecting all matching pixels across canvas
    - [x] Implement Feature: Scan all pixels, select those within color tolerance
- [x] Task: Add alpha channel selection handler
    - [x] Write Tests: E2E tests selecting by alpha range
    - [x] Implement Feature: Scan alpha channel, create selection mask from alpha values

## Phase 3: CLI & MCP Support [pending_commit]
- [x] Task: Add CLI subcommands for color and alpha selection
    - [x] Write Tests: Unit tests for CLI argument parsing
    - [x] Implement Feature: Add `krita selection color` and `krita selection alpha` subcommands
- [x] Task: Add MCP tools for color and alpha selection
    - [x] Write Tests: Unit tests for FastMCP tool registration
    - [x] Implement Feature: Register `krita_select_by_color` and `krita_select_by_alpha` in MCP server
