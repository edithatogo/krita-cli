# Krita API Coverage Matrix

This document compares four surfaces:

1. The plugin dispatch table in `krita-plugin/kritamcp/__init__.py`, which is the wrapped Krita action surface used here as the practical baseline for this project.
2. The current `krita` CLI.
3. The current FastMCP server.
4. The earlier `krita-mcp` MCP server surface at commit `0ae7381`.

This is intentionally source-derived rather than README-derived.

## Method

- Baseline plugin-backed actions: `krita-plugin/kritamcp/__init__.py`
- Current CLI entrypoints: `src/krita_cli/app.py` plus `src/krita_cli/commands/*.py`
- Current MCP tools: `src/krita_mcp/server.py`
- Legacy MCP baseline: `git show 0ae7381:src/krita_mcp/server.py`

## Summary

- Plugin-backed action baseline: `52` actions
- Current CLI coverage of plugin-backed actions: `52/52`
- Current MCP coverage of plugin-backed actions: `52/52`
- Legacy MCP coverage of plugin-backed actions at `0ae7381`: `20/52`

Current notes worth knowing up front:

- CLI and MCP now both cover the full plugin-backed action baseline
- `combine_selections` is implemented as a real composition step using the active selection plus a second selection loaded from a mask file
- `select_area` in both the CLI and MCP server is still a compatibility alias over rectangle selection rather than a dedicated client method

## Plugin-Backed Coverage

Legend:

- `CLI command`: exact command path exposed by `krita`
- `Current MCP`: exact tool name in `src/krita_mcp/server.py`
- `Legacy MCP`: exact tool name present in legacy commit `0ae7381`
- `-`: not exposed on that surface

### Core Canvas And Painting

| Plugin action | CLI command | Current MCP | Legacy MCP |
|---|---|---|---|
| `new_canvas` | `krita canvas new-canvas` | `krita_new_canvas` | `krita_new_canvas` |
| `set_color` | `krita color set-color` | `krita_set_color` | `krita_set_color` |
| `set_brush` | `krita brush set-brush` | `krita_set_brush` | `krita_set_brush` |
| `stroke` | `krita stroke stroke` | `krita_stroke` | `krita_stroke` |
| `fill` | `krita stroke fill` | `krita_fill` | `krita_fill` |
| `draw_shape` | `krita stroke draw-shape` | `krita_draw_shape` | `krita_draw_shape` |
| `get_canvas` | `krita canvas get-canvas` | `krita_get_canvas` | `krita_get_canvas` |
| `undo` | `krita navigation undo` | `krita_undo` | `krita_undo` |
| `redo` | `krita navigation redo` | `krita_redo` | `krita_redo` |
| `clear` | `krita canvas clear` | `krita_clear` | `krita_clear` |
| `save` | `krita canvas save` | `krita_save` | `krita_save` |
| `get_color_at` | `krita color get-color-at` | `krita_get_color_at` | `krita_get_color_at` |
| `list_brushes` | `krita brush list-brushes` | `krita_list_brushes` | `krita_list_brushes` |
| `open_file` | `krita file open-file` | `krita_open_file` | `krita_open_file` |

### Automation And Inspection

| Plugin action | CLI command | Current MCP | Legacy MCP |
|---|---|---|---|
| `batch` | `krita batch` | `krita_batch` | `krita_batch` |
| `rollback` | `krita rollback` | `krita_rollback` | `krita_rollback` |
| `get_command_history` | `krita history` | `krita_get_command_history` | `krita_get_command_history` |
| `get_canvas_info` | `krita introspect canvas-info` | `krita_get_canvas_info` | `krita_get_canvas_info` |
| `get_current_color` | `krita introspect current-color` | `krita_get_current_color` | `krita_get_current_color` |
| `get_current_brush` | `krita introspect current-brush` | `krita_get_current_brush` | `krita_get_current_brush` |
| `get_capabilities` | `krita introspect capabilities` | `krita_get_capabilities` | `-` |
| `get_security_status` | `krita selection security-status` | `krita_security_status` | `-` |

### Layers

| Plugin action | CLI command | Current MCP | Legacy MCP |
|---|---|---|---|
| `list_layers` | `krita layers list` | `krita_list_layers` | `-` |
| `create_layer` | `krita layers create` | `krita_create_layer` | `-` |
| `select_layer` | `krita layers select` | `krita_select_layer` | `-` |
| `delete_layer` | `krita layers delete` | `krita_delete_layer` | `-` |
| `rename_layer` | `krita layers rename` | `krita_rename_layer` | `-` |
| `set_layer_opacity` | `krita layers set-opacity` | `krita_set_layer_opacity` | `-` |
| `set_layer_visibility` | `krita layers set-visibility` | `krita_set_layer_visibility` | `-` |

### Selection Geometry And Editing

| Plugin action | CLI command | Current MCP | Legacy MCP |
|---|---|---|---|
| `select_rect` | `krita selection select-rect` | `krita_select_rect` | `-` |
| `select_ellipse` | `krita selection select-ellipse` | `krita_select_ellipse` | `-` |
| `select_polygon` | `krita selection select-polygon` | `krita_select_polygon` | `-` |
| `select_area` | `krita selection select-area` | `krita_select_area` | `-` |
| `selection_info` | `krita selection select-info` | `krita_selection_info` | `-` |
| `clear_selection` | `krita selection select-clear` | `krita_clear_selection` | `-` |
| `fill_selection` | `krita selection select-fill` | `krita_fill_selection` | `-` |
| `invert_selection` | `krita selection select-invert` | `krita_invert_selection` | `-` |
| `deselect` | `krita selection deselect` | `krita_deselect` | `-` |
| `select_by_color` | `krita selection select-by-color` | `krita_select_by_color` | `-` |
| `select_by_alpha` | `krita selection select-by-alpha` | `krita_select_by_alpha` | `-` |
| `combine_selections` | `krita selection combine-selections` | `krita_combine_selections` | `-` |

### Selection Transforms And Persistence

| Plugin action | CLI command | Current MCP | Legacy MCP |
|---|---|---|---|
| `transform_selection` | `krita selection transform-selection` | `krita_transform_selection` | `-` |
| `grow_selection` | `krita selection grow-selection` | `krita_grow_selection` | `-` |
| `shrink_selection` | `krita selection shrink-selection` | `krita_shrink_selection` | `-` |
| `border_selection` | `krita selection border-selection` | `krita_border_selection` | `-` |
| `save_selection` | `krita selection save-selection` | `krita_save_selection` | `-` |
| `load_selection` | `krita selection load-selection` | `krita_load_selection` | `-` |
| `selection_stats` | `krita selection selection-stats` | `krita_selection_stats` | `-` |
| `save_selection_channel` | `krita selection save-channel` | `krita_save_selection_channel` | `-` |
| `load_selection_channel` | `krita selection load-channel` | `krita_load_selection_channel` | `-` |
| `list_selection_channels` | `krita selection list-channels` | `krita_list_selection_channels` | `-` |
| `delete_selection_channel` | `krita selection delete-channel` | `krita_delete_selection_channel` | `-` |

## Helper Surfaces Outside The Plugin Action Baseline

These are important, but they should not be confused with wrapped Krita action coverage.

### Compatibility Aliases

| Surface | Name | Backing behavior |
|---|---|---|
| CLI | `krita selection select-area` | Calls `select_rect` through the typed client |
| MCP | `krita_select_area` | Calls `select_rect` through the typed client |

### CLI-Only Helpers

| CLI command | Notes |
|---|---|
| `krita health` | Connectivity/status helper, not a plugin dispatch action |
| `krita call` | Raw command passthrough helper |
| `krita replay` | Replays command files, not a first-class plugin action |
| `krita config show` | Local config helper |
| `krita config set` | Local config helper |
| `krita config reset` | Local config helper |

### MCP-Only Helpers

| MCP tool | Notes |
|---|---|
| `krita_health` | Connectivity/status helper, not part of the plugin action dispatch table |
| `krita_list_tools` | Server self-description helper |

## Practical Readout

- The current MCP server now matches the CLI across the stable, agent-useful wrapped actions: painting, introspection, layers, selection geometry, transforms, and selection persistence.
- CLI and MCP now both cover the full plugin-backed baseline.
- `combine_selections` is no longer a paper-only parity item: it combines the active selection with a second selection sourced from a mask file, which keeps the public behavior explicit and testable.
