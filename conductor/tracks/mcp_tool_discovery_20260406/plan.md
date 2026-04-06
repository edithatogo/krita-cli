# Implementation Plan: MCP Tool Discovery

## Phase 1: Tool Registry & Listing
- [ ] Task: Create central tool registry
    - [ ] Write Tests: Unit tests for tool registry (add, list, get by name)
    - [ ] Implement Feature: Create `ToolRegistry` class in `src/krita_mcp/` that stores tool metadata
- [ ] Task: Implement `krita_list_tools` MCP tool
    - [ ] Write Tests: Unit tests for tool listing output format
    - [ ] Implement Feature: Register `krita_list_tools` in MCP server

## Phase 2: Versioning & Capabilities
- [ ] Task: Add tool versioning to registry
    - [ ] Write Tests: Unit tests for version negotiation
    - [ ] Implement Feature: Add version field to all registered tools
- [ ] Task: Add plugin capabilities endpoint
    - [ ] Write Tests: Integration tests for capabilities response
    - [ ] Implement Feature: Add `/capabilities` endpoint to plugin HTTP server

## Phase 3: Integration
- [ ] Task: Integrate tool registry with FastMCP
    - [ ] Write Tests: Integration test verifying all tools appear in listing
    - [ ] Implement Feature: Wire tool registry to FastMCP tool registration
