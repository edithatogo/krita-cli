# Track Specification: Selection Transforms & Modifiers

## Phase 11b: Selection Tools — Extended Operations

### Problem Statement

After the initial Selection Tools track, agents and users can create selections but cannot modify or transform them without starting over. Standard image editors support transform and modifier operations that are essential for iterative selection refinement.

### Requirements

1. **Transform Operations** — Move (translate), rotate, and scale an existing selection boundary without affecting canvas pixels.
2. **Selection Modifiers** — Grow (expand by N pixels), shrink (contract by N pixels), and border (create a band of N pixels around the selection edge).
3. **Selection Combiners** — Union (combine two selections), intersect (keep only overlapping area), subtract (remove one selection from another).
4. **CLI Commands** — `krita selection transform`, `krita selection grow`, `krita selection shrink`, `krita selection border`, `krita selection union`, `krita selection intersect`, `krita selection subtract`.
5. **MCP Tools** — `krita_transform_selection`, `krita_grow_selection`, `krita_shrink_selection`, `krita_border_selection`, `krita_combine_selections`.

### Acceptance Criteria

- [ ] Move/rotate/scale selection without modifying canvas pixels
- [ ] Grow/shrink/border operations work correctly
- [ ] Union/intersect/subtract operations combine selections correctly
- [ ] CLI subcommands documented and functional
- [ ] MCP tools registered and discoverable
- [ ] All new code passes lint, type check, and test suites
- [ ] Unit, integration, and property-based tests added
