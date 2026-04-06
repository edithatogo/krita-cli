# Implementation Plan: Selection Transforms & Modifiers

## Phase 1: Core Models & Client
- [ ] Task: Define Pydantic models for transform and modifier operations
    - [ ] Write Tests: Unit tests for TransformParams, GrowParams, ShrinkParams, BorderParams, CombineParams
    - [ ] Implement Feature: Add models in `src/krita_client/models.py`
- [ ] Task: Add HTTP handlers for transform and modifier operations
    - [ ] Write Tests: Integration tests using `pytest-httpx` for all endpoints
    - [ ] Implement Feature: Add client methods in `src/krita_client/client.py`

## Phase 2: Krita Plugin Integration
- [ ] Task: Add transform handlers (move, rotate, scale)
    - [ ] Write Tests: E2E tests verifying selection bounds change after transform
    - [ ] Implement Feature: Update plugin to use Krita's selection transform APIs
- [ ] Task: Add modifier handlers (grow, shrink, border)
    - [ ] Write Tests: E2E tests verifying pixel-level changes after modifiers
    - [ ] Implement Feature: Use Krita's selection grow/shrink/border APIs
- [ ] Task: Add combiner handlers (union, intersect, subtract)
    - [ ] Write Tests: E2E tests for all three combination operations
    - [ ] Implement Feature: Use Krita's selection combination APIs

## Phase 3: CLI & MCP Support
- [ ] Task: Add CLI subcommands for transforms and modifiers
    - [ ] Write Tests: Unit tests for CLI argument parsing
    - [ ] Implement Feature: Add `krita selection` command group with transform, grow, shrink, border, union, intersect, subtract subcommands
- [ ] Task: Add MCP tools for transforms and modifiers
    - [ ] Write Tests: Unit tests for FastMCP tool registration
    - [ ] Implement Feature: Register `krita_transform_selection`, `krita_grow_selection`, `krita_shrink_selection`, `krita_border_selection`, `krita_combine_selections` in MCP server
