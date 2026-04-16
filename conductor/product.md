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
1. **Krita Plugin** — Python plugin inside Krita, HTTP server on localhost:5678, executes paint commands on Krita's main thread via command queue.
2. **Core Client** (`krita_client`) — Shared typed HTTP client with pydantic models for all commands.
3. **Interfaces** — CLI (typer) and MCP server (fastmcp), both import from core client.

## Current Tools (40 total)

| Category | capabilities |
|----------|--------------|
| **Core** | Canvas creation, file management, health checks |
| **Painting** | Strokes, fills, shapes, brush/color management |
| **Selection** | Geometric, color-based, and alpha-based selections |
| **Selection Ops**| Transforms (rotate/scale/move), grow/shrink, combination ops |
| **Persistence** | Selection masks (PNG), named selection channels |
| **Session** | History logging, command replay, rollback/undo/redo, batching |
| **Inspection** | Canvas info, eyedropper, selection stats, security status |

## Release 1.0.0 (COMPLETED)

All development phases are complete:

- [x] **Phase 1-10 Foundation**: Scaffolding, Core Client, Plugin IPC, Basic CLI/MCP.
- [x] **Phase 11a Protocol & Config**: Versioning, structured errors, config CLI.
- [x] **Phase 11b Layers & Canvas**: Full layer management and canvas introspection.
- [x] **Phase 11c Selection Suite**: 20+ selection-related tools and persistence.
- [x] **Phase 11d Session management**: Batching, History, Replay, and Rollback.
- [x] **Phase 12 Integration**: E2E testing, CLI grouping, Windows validation.
- [x] **Quality Gate**: 95.00% test coverage reached.

## Next Steps

- Release v1.0.0 to PyPI
- Community feedback and feature requests
- Support for Krita's native brush engines in strokes
