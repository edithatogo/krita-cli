# Krita MCP — Product Context

## What is this?

A **SOTA CLI + MCP server** for programmatic painting in Krita. Two interfaces, one core:
- **CLI**: `krita stroke --points 100,100 200,200` — direct command-line control
- **MCP**: FastMCP server — for AI agents (Claude, etc.) to paint programmatically

Both talk to a Krita plugin via HTTP on localhost:5678.

## Problem it solves

AI models can generate images but can't directly interact with desktop painting applications. This project closes that gap — letting AI agents OR humans control Krita's canvas in real time, see their work via PNG exports, and iterate on paintings.

## Users

- **AI agents** (Claude, etc.) via MCP protocol
- **Developers/Artists** via CLI for scripting, automation, batch operations
- **CI/CD pipelines** for automated image generation

## Architecture

```
CLI (typer)     ↘
                  →  krita_client (pydantic models + HTTP client)  →  Krita Plugin (HTTP :5678)  →  Krita
MCP (fastmcp)   ↗
```

Three layers:
1. **Krita Plugin** — Python plugin inside Krita, HTTP server on localhost:5678, executes paint commands on Krita's main thread via command queue
2. **Core Client** (`krita_client`) — Shared typed HTTP client with pydantic models for all commands
3. **Interfaces** — CLI (typer) and MCP server (fastmcp), both import from core client

## Current Tools (16+ total)

| Tool | What it does |
|------|-------------|
| `krita_health` | Check Krita + plugin status |
| `krita_new_canvas` | Create canvas (width, height, bg color) |
| `krita_set_color` | Set foreground color (hex) |
| `krita_set_brush` | Set brush preset/size/opacity |
| `krita_stroke` | Paint stroke through [x, y] points |
| `krita_fill` | Fill circular area |
| `krita_draw_shape` | Draw rectangle/ellipse/line |
| `krita_get_canvas` | Export canvas to PNG |
| `krita_save` | Save canvas to file |
| `krita_undo` / `krita_redo` | Undo/redo |
| `krita_clear` | Clear canvas |
| `krita_get_color_at` | Eyedropper |
| `krita_list_brushes` | List brush presets |
| `krita_open_file` | Open existing file |
| `krita_batch` | Execute multiple commands sequentially |
| `krita_rollback` | Roll back a batch operation by batch ID |
| `krita_select_rect` | Select a rectangular area |
| `krita_select_ellipse` | Select an elliptical area |
| `krita_select_polygon` | Select a polygonal area |
| `krita_selection_info` | Get current selection bounds |
| `krita_invert_selection` | Invert the current selection |
| `krita_clear_selection` | Clear selection contents |
| `krita_fill_selection` | Fill selection with foreground color |
| `krita_deselect` | Remove current selection |
| `krita_transform_selection` | Move/rotate/scale selection boundary |
| `krita_grow_selection` | Grow selection by N pixels |
| `krita_shrink_selection` | Shrink selection by N pixels |
| `krita_border_selection` | Create border selection |
| `krita_combine_selections` | Union/intersect/subtract selections |
| `krita_select_by_color` | Magic wand/global color selection |
| `krita_select_by_alpha` | Select by transparency range |
| `krita_save_selection` | Save selection as PNG mask |
| `krita_load_selection` | Load selection from PNG mask |
| `krita_selection_stats` | Get selection statistics |
| `krita_save_selection_channel` | Save selection as named channel |
| `krita_load_selection_channel` | Load named selection channel |
| `krita_list_selection_channels` | List saved selection channels |

## Completed (Phases 1-10)

- [x] Project scaffolding with uv, ruff, ty, pytest, pre-commit, renovate, CI/CD
- [x] Core client library with pydantic validation, typed HTTP client, OpenAPI schema
- [x] CLI with 16 subcommands + raw JSON mode + rich output
- [x] MCP server refactored to import from krita_client
- [x] Krita plugin fixed (race condition, thread safety, OOM limits, path sanitization, numpy rendering)
- [x] 240 tests, 99.55% coverage (unit, integration, property-based, E2E skeleton)
- [x] CI/CD pipeline with automated releases
- [x] Performance benchmarks and numpy-accelerated rendering
- [x] Comprehensive Krita API type stubs
- [x] All lint/type/test checks passing
- [x] Batch operations endpoint end-to-end

## Next (Phase 11+)

**Phase 11a: Protocol & Config**
- [x] Protocol versioning
- [x] Structured error responses
- [x] Plugin config CLI

**Phase 11b: Layers & Canvas**
- [/] Canvas state introspection (Client/CLI done)
- [/] Layer management (Client/CLI done)
- [x] Selection tools
- [ ] Security & limits validation

**Phase 11c: Batch & History**
- [x] Command history log
- [x] Replay CLI integration
- [x] Rollback mechanisms (for failed batch/replay)

