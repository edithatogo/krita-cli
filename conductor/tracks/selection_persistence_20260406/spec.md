# Track Specification: Selection Persistence & Session Management

## Phase 11b: Selection Tools — Save/Load & Session Continuity

### Problem Statement

Currently, selections are lost when Krita restarts or when a new session begins. This breaks agent workflows that span multiple sessions and prevents users from reusing complex selections. Additionally, the batch operations endpoint does not account for selection-dependent behavior.

### Requirements

1. **Selection Save/Load** — Export the current selection mask as a PNG image. Load a saved selection mask from an image file and restore it as an active selection on the canvas.
2. **Selection Channels** — Save selections as named alpha channels within the current document. List, load, and delete saved channels.
3. **Selection Metadata** — Get selection statistics: pixel count, centroid coordinates, bounding box, area percentage of canvas.
4. **Batch Selection Awareness** — Document and test that `krita batch` operations clip to the active selection. Add optional `respect_selection` flag to batch requests.
5. **CLI Commands** — `krita selection save`, `krita selection load`, `krita selection channels`, `krita selection stats`.
6. **MCP Tools** — `krita_save_selection`, `krita_load_selection`, `krita_list_selection_channels`, `krita_selection_stats`.

### Acceptance Criteria

- [ ] Selection can be exported as PNG mask (white=selected, black=unselected)
- [ ] Selection can be loaded from PNG mask and restored on canvas
- [ ] Selections can be saved as named channels within the document
- [ ] Selection statistics (pixel count, centroid, bounding box, area %) returned accurately
- [ ] Batch operations documented and tested with selection clipping behavior
- [ ] CLI subcommands documented and functional
- [ ] MCP tools registered and discoverable
- [ ] All new code passes lint, type check, and test suites
