# Implementation Plan: CLI Command Grouping

## Phase 1: Design & Planning
- [ ] Task: Design command group structure
    - [ ] Implement Feature: Document proposed group mapping (existing command → grouped command)
- [ ] Task: Create command group Typer apps
    - [ ] Write Tests: Unit tests for each group app's help output
    - [ ] Implement Feature: Create `krita canvas`, `krita brush`, `krita selection`, `krita file`, `krita layer` group apps

## Phase 2: Migration & Backward Compatibility
- [ ] Task: Add backward-compatible aliases
    - [ ] Write Tests: Tests verifying old commands still work with deprecation warnings
    - [ ] Implement Feature: Register flat commands as deprecated aliases pointing to grouped commands
- [ ] Task: Update all CLI tests to use grouped commands
    - [ ] Implement Feature: Update integration tests to test both old and new command paths

## Phase 3: Documentation & CI
- [ ] Task: Update help text and documentation
    - [ ] Implement Feature: Ensure `krita --help` shows groups; each group shows subcommands
- [ ] Task: Update README with new CLI structure
    - [ ] Implement Feature: Update product.md with new command table
