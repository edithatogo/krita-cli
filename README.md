# Krita MCP Server & CLI

Let AI agents paint in [Krita](https://krita.org/) via the [Model Context Protocol](https://modelcontextprotocol.io/).

This subproject provides the core implementation of the Krita-MCP ecosystem, including the FastMCP server, the `krita` CLI, and the high-performance Python plugin.

## 📦 Packages

- **PyPI**: [`krita-cli`](https://pypi.org/project/krita-cli/)
- **Conda**: [`doughnut/krita-cli`](https://anaconda.org/doughnut/krita-cli)

## 🛠️ Components

1. **Krita Plugin** (`krita-plugin/`) — A Python plugin for Krita that exposes a thread-safe HTTP server on `localhost` using the configured port (default `5678`).
2. **MCP Server** (`src/krita_mcp/`) — A FastMCP server exposing 50+ painting and manipulation tools.
3. **Krita CLI** (`src/krita_cli/`) — A Typer-based command line interface for human operators.
4. **Krita Client** (`src/krita_client/`) — A reusable, fully-typed Python library for Krita automation.

## 🚀 Install

### 1. Install the CLI / client package

Pick one package source:

```bash
pip install krita-cli
```

```bash
uv tool install krita-cli
```

```bash
conda install doughnut::krita-cli
```

The published package gives you the `krita` CLI, the Python client library, and the MCP server entry points. It does **not** install the desktop Krita plugin for you.

### 2. Install the Krita desktop plugin

Copy the contents of `krita-plugin/` to your Krita resources:
- **Windows**: `%APPDATA%\krita\pykrita\`
- **Linux**: `~/.local/share/krita/pykrita/`
- **macOS**: `~/Library/Application Support/krita/pykrita/`

Enable **"Krita MCP Bridge"** in Krita (Configure Krita → Python Plugin Manager) and restart.

### 3. Development environment setup
```bash
# Install dependencies with uv
uv sync
```

### 4. Windows validation checklist
Before debugging the plugin, make sure the local Python runtime is healthy:

1. `python -c "import ssl, ctypes"` must succeed.
2. `python scripts/windows_preflight.py` should report a clean Windows setup.
3. `uv run pytest tests/e2e/test_e2e_mock.py` should pass without Krita.
4. The plugin files must exist under `%APPDATA%\krita\pykrita\kritamcp\`.
5. Krita must be restarted after enabling **Krita MCP Bridge** in the Plugin Manager.
6. The plugin should expose `http://127.0.0.1:<configured-port>/health` once Krita finishes loading.

If Krita starts but `/health` never appears, check the diagnostic artifacts in your home directory:
- `~/kritamcp_startup.log`
- `~/kritamcp_diag.log`

If those logs are missing entirely, the plugin likely was not enabled or did not load during startup.

## 🔧 CLI Commands

The `krita` CLI is grouped into logical subcommands:

- **Painting**: `stroke`, `fill`, `clear`, `draw-shape`
- **Layers**: `layers list`, `layers create`, `layers select`, `layers delete`
- **Selection**: `selection select-rect`, `selection transform`, `selection save-channel`
- **Canvas**: `canvas-info`, `current-color`, `current-brush`
- **Session**: `history`, `replay`, `rollback`, `batch`
- **System**: `health`, `config`, `capabilities`, `security-status`

Run `uv run krita --help` for full details.

## 🧪 Example Workflow

The latest end-to-end workflow in this repo was an intentionally iterative "pelican on a bike" exercise used to harden the toolchain and the operator workflow:

1. Start with a rough drawing and save it as version 1 instead of overwriting it.
2. Promote repeated prompting and review behavior into a dedicated agent and `SKILL.md`.
3. Study pelican references before redrawing so anatomy, posture, and proportions improve deliberately.
4. Save every numbered iteration, compare them, and write down what changed.
5. Archive the outputs and generate an animation/contact sheet to review the progression.

Repo artifacts for that workflow:

- [Learning log](notes/pelican-bike-learning-log.md)
- [Pelican bike agent](.codex-plugin/agents/pelican-bike-illustrator.md)
- [Pelican bike skill](.codex-plugin/skills/pelican-bike-drawing/SKILL.md)
- [Pelican anatomy reference notes](.codex-plugin/skills/pelican-bike-drawing/references/pelican-anatomy.md)

## 🤖 MCP Server Tools (54 Declared Tools)

For the exact source-derived command-by-command comparison between the plugin action surface, the current CLI, the current MCP server, and the earlier legacy `krita-mcp` server surface, see [docs/api-coverage-matrix.md](docs/api-coverage-matrix.md).

For the broader question of whether the entire Krita API should be mapped, see [docs/krita-api-inventory.md](docs/krita-api-inventory.md).

For the recommendation on where MCP should and should not track CLI parity, see [docs/cli-mcp-parity-assessment.md](docs/cli-mcp-parity-assessment.md).

The MCP server exposes a vast range of capabilities to AI agents:

| Category | Key Tools |
|----------|-----------|
| **Core** | `krita_health`, `krita_new_canvas`, `krita_save`, `krita_open_file` |
| **Painting** | `krita_stroke`, `krita_fill`, `krita_draw_shape`, `krita_set_color`, `krita_set_brush` |
| **Selection** | `krita_select_rect`, `krita_select_ellipse`, `krita_select_polygon`, `krita_selection_info`, `krita_deselect` |
| **Selection Ops** | `krita_transform_selection`, `krita_grow_selection`, `krita_shrink_selection`, `krita_border_selection`, `krita_combine_selections`, `krita_invert_selection`, `krita_fill_selection` |
| **Persistence** | `krita_save_selection`, `krita_load_selection`, `krita_save_selection_channel`, `krita_list_selection_channels` |
| **Automation** | `krita_batch`, `krita_rollback`, `krita_get_command_history`, `krita_list_tools` |
| **Inspection** | `krita_get_canvas_info`, `krita_get_color_at`, `krita_selection_stats`, `krita_security_status`, `krita_get_capabilities` |

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
