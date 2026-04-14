# Track Specification: Selection Advanced Features

## Phase 11b: Selection Tools — Color & Alpha Selection

### Problem Statement

Current selection tools are geometry-based (rect, ellipse, polygon). AI agents and users often need to select by content — specific colors, color ranges, or transparency levels. These are standard features in all image editors but are missing from the Krita MCP toolset.

### Requirements

1. **Color-Based Selection (Magic Wand)** — Select contiguous regions by color similarity from a seed point. Tolerance threshold controls how similar adjacent pixels must be to be included.
2. **Global Color Selection** — Select all pixels matching a color range across the entire canvas (not just contiguous regions).
3. **Alpha Channel Selection** — Select based on transparency: select all opaque pixels, all transparent pixels, or a range of alpha values.
4. **Color Selection with Layer Scope** — Select by color on a specific layer, all visible layers, or a layer group.
5. **CLI Commands** — `krita selection color`, `krita selection alpha`.
6. **MCP Tools** — `krita_select_by_color`, `krita_select_by_alpha`.

### Acceptance Criteria

- [ ] Magic wand selects contiguous region within tolerance from seed point
- [ ] Global color selection selects matching pixels across entire canvas
- [ ] Alpha selection selects pixels within alpha range
- [ ] Tolerance/range parameters validated via pydantic
- [ ] CLI subcommands documented and functional
- [ ] MCP tools registered and discoverable
- [ ] All new code passes lint, type check, and test suites
- [ ] Unit, integration, and property-based tests added
