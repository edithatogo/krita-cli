# Krita MCP — Tech Stack

## Languages & Runtimes

- **Python >=3.12** — Both the MCP server, CLI, and Krita plugin are written in Python
- Krita's embedded Python interpreter runs the plugin

## Package Management

- **uv** — Package manager by Astral. 10-100x faster than pip.

## Dependencies

### Core Client (`krita_client`)
- **pydantic v2** — Data validation, serialization, JSON schema generation
- **pydantic-settings** — Centralized config management with env var support
- **httpx** — Async HTTP client for communicating with Krita plugin

### MCP Server (`krita_mcp`)
- **fastmcp** — MCP server framework
- Imports core logic from `krita_client`

### CLI (`krita_cli`)
- **typer** — Type-hint driven CLI framework
- **rich** — Beautiful terminal output

### Krita Plugin (`krita-plugin/`)
- Uses Krita's built-in Python API (`krita`, `PyQt5.QtCore`, etc.)
- Standard library: `http.server`, `threading`, `json`, `time`, `os`, `itertools`, `math`
- Optional: **numpy** for accelerated pixel rendering

### Dev Tooling
- **ruff** — Linting + formatting (strict mode)
- **ty** — Type checking by Astral (100% coverage)
- **pytest** + **pytest-xdist** — Testing with parallel execution
- **pytest-cov** — Coverage tracking (100% required)
- **pytest-asyncio** — Async test support
- **pytest-httpx** — HTTP mocking
- **hypothesis** — Property-based testing
- **mutmut** — Mutation testing
- **pre-commit** — Git hooks
- **scalene** — Profiling
- **python-semantic-release** — Automated PyPI releases

## Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | All dependencies, tool configs, entry points |
| `src/krita_client/` | Core client library |
| `src/krita_mcp/` | MCP server |
| `src/krita_cli/` | CLI interface |
| `krita-plugin/kritamcp/__init__.py` | Krita plugin |
| `types/krita/__init__.pyi` | Type stubs for Krita API |

## Communication Protocol

- **HTTP POST** to `localhost:5678` with JSON body: `{"action": "...", "params": {...}}`
- **HTTP GET** to `localhost:5678/health` for health checks
- Default timeout: 30s for most commands, 120s for export/save

## Configuration

| Setting | Default | Where |
|---------|---------|-------|
| Plugin HTTP port | `5678` | `krita-plugin/kritamcp/__init__.py` |
| MCP server URL | `http://localhost:5678` | `krita_client` config (env var `KRITA_URL`) |
| Canvas output dir | `~/krita-mcp-output` | `krita-plugin/kritamcp/__init__.py` |
| Max canvas dimensions | `8192x8192` | `krita_client` models + plugin validation |
| Max batch snapshots | `50` | `krita-plugin/kritamcp/snapshot_store.py` |

## Testing Strategy

| Layer | Tool | What |
|-------|------|------|
| Unit | `pytest` | Individual functions in `krita_client` |
| Integration | `pytest` + `pytest-httpx` | MCP tools + CLI with mocked HTTP |
| E2E | `pytest` | Full flow with actual Krita plugin |
| Property-based | `hypothesis` | Edge cases for all inputs |
| Mutation | `mutmut` | Ensures tests catch bugs |

Coverage: 95% required. Type coverage: 100% required (enforced by ty on src/ and types/).

## Current State (Phases 1-10 Complete)

| Metric | Value |
|--------|-------|
| Tests | 320 passed |
| Coverage | ~70% (increased count) |
| Type check | All passed |
| Lint | All passed |
| Format | 33 files formatted |

## File Structure

```
krita-cli/
├── conductor/                    ← Conductor context and tracks
│   ├── product.md
│   ├── tech-stack.md
│   ├── workflow.md
│   └── tracks/
│       └── phase-11-features/    ← Next track (pending)
│           └── spec.md
├── krita-mcp/
│   ├── krita_plugin/             ← Krita plugin (fixed)
│   ├── src/
│   │   ├── krita_client/         ← Core client library
│   │   ├── krita_mcp/            ← MCP server
│   │   └── krita_cli/            ← CLI interface
│   ├── types/krita/              ← Comprehensive type stubs
│   ├── tests/                    ← 240 tests
│   ├── benchmarks/               ← Performance benchmarks
│   ├── pyproject.toml            ← All tool configs
│   ├── uv.lock
│   ├── .pre-commit-config.yaml
│   ├── renovate.json
│   └── .github/workflows/ci.yml
```
