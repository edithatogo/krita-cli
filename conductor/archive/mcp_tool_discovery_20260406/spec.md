# Track Specification: MCP Tool Discovery

## Phase 12: MCP Server Enhancement

### Problem Statement

Currently, AI agents must know tool names in advance to use them. There is no self-discovery mechanism for available tools. This limits the agent's ability to adapt to new features (like selection tools) without explicit reconfiguration.

### Requirements

1. **Tool Listing MCP Tool** — Add `krita_list_tools` MCP tool that returns all available tools with names, descriptions, and parameter schemas.
2. **Tool Versioning** — Each tool reports its version. Agents can check compatibility before calling.
3. **Capability Negotiation** — The plugin reports its capabilities (selection support, layer support, batch support) so agents know what operations are available.
4. **Dynamic Tool Registration** — Tools are registered in a central registry that the listing tool queries.

### Acceptance Criteria

- [ ] `krita_list_tools` returns complete tool inventory with descriptions
- [ ] Tool versioning included in listing response
- [ ] Plugin capabilities reported in health/status endpoint
- [ ] Unit and integration tests for discovery endpoints
- [ ] All new code passes lint, type check, and test suites
