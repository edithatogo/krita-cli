# Implementation Plan: CLI Command Grouping

## Phase 1: Design & Planning
- [x] Task: Design command group structure
    - [x] Implement Feature: Document proposed group mapping (existing command → grouped command)
- [x] Task: Create command group Typer apps
    - [x] Write Tests: Unit tests for each group app's help output
    - [x] Implement Feature: Create `krita canvas`, `krita brush`, `krita selection`, `krita file`, `krita layer` group apps

## Phase 2: Migration & Backward Compatibility
- [x] Task: Add backward-compatible aliases
    - [x] Write Tests: Tests verifying old commands still work with deprecation warnings
    - [x] Implement Feature: Register flat commands as deprecated aliases pointing to grouped commands
- [x] Task: Update all CLI tests to use grouped commands
    - [x] Implement Feature: Update integration tests to test both old and new command paths

## Phase 3: Documentation & CI
- [x] Task: Update help text and documentation
    - [x] Implement Feature: Ensure `krita --help` shows groups; each group shows subcommands
- [x] Task: Update README with new CLI structure
    - [x] Implement Feature: Update product.md with new command table
