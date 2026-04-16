# Krita MCP Server & CLI

Let AI agents paint in [Krita](https://krita.org/) via the [Model Context Protocol](https://modelcontextprotocol.io/).

This subproject provides the core implementation of the Krita-MCP ecosystem, including the FastMCP server, the `krita` CLI, and the high-performance Python plugin.

## 🛠️ Components

1. **Krita Plugin** (`krita-plugin/`) — A Python plugin for Krita that exposes a thread-safe HTTP server on `localhost:5678`.
2. **MCP Server** (`src/krita_mcp/`) — A FastMCP server exposing 40+ painting and manipulation tools.
3. **Krita CLI** (`src/krita_cli/`) — A Typer-based command line interface for human operators.
4. **Krita Client** (`src/krita_client/`) — A reusable, fully-typed Python library for Krita automation.

## 🚀 Setup

### 1. Krita Plugin Installation
Copy the contents of `krita-plugin/` to your Krita resources:
- **Windows**: `%APPDATA%\krita\pykrita\`
- **Linux**: `~/.local/share/krita/pykrita/`
- **macOS**: `~/Library/Application Support/krita/pykrita/`

Enable **"Krita MCP Bridge"** in Krita (Configure Krita → Python Plugin Manager) and restart.

### 2. Environment Setup
```bash
# Install dependencies with uv
uv sync
```

## 🔧 CLI Commands

The `krita` CLI is grouped into logical subcommands:

- **Painting**: `stroke`, `fill`, `clear`, `draw-shape`
- **Layers**: `layers list`, `layers create`, `layers select`, `layers delete`
- **Selection**: `selection select-rect`, `selection transform`, `selection save-channel`
- **Canvas**: `canvas-info`, `current-color`, `current-brush`
- **Session**: `history`, `replay`, `rollback`, `batch`
- **System**: `health`, `config`, `capabilities`, `security-status`

Run `uv run krita --help` for full details.

## 🤖 MCP Server Tools (40 Total)

The MCP server exposes a vast range of capabilities to AI agents:

| Category | Key Tools |
|----------|-----------|
| **Core** | `krita_health`, `krita_new_canvas`, `krita_save`, `krita_open_file` |
| **Painting** | `krita_stroke`, `krita_fill`, `krita_draw_shape`, `krita_set_color`, `krita_set_brush` |
| **Selection** | `krita_select_rect`, `krita_select_ellipse`, `krita_select_polygon`, `krita_select_by_color`, `krita_select_by_alpha` |
| **Selection Ops** | `krita_transform_selection`, `krita_grow_selection`, `krita_combine_selections`, `krita_invert_selection` |
| **Persistence** | `krita_save_selection`, `krita_load_selection`, `krita_save_selection_channel`, `krita_list_selection_channels` |
| **Automation** | `krita_batch`, `krita_rollback`, `krita_get_command_history` |
| **Inspection** | `krita_get_canvas_info`, `krita_get_color_at`, `krita_selection_stats`, `krita_security_status` |

## ⚡ Performance

The plugin uses **numpy-accelerated** direct pixel manipulation for rendering. This ensures that strokes and shapes are rendered significantly faster than standard Python loops, especially on high-resolution canvases.

## 🔒 Security

Krita MCP includes a built-in security layer to protect your system:
- **Path Sanitization**: Restricts file operations to allowed directories.
- **Resource Limits**: Prevents OOM by limiting max canvas dimensions and layer counts.
- **Rate Limiting**: Throttles rapid command execution.
- **Security Tool**: `krita_security_status` allows agents to check active limits.

## 📄 License
MIT
