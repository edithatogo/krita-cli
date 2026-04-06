# Krita MCP — Workflow

## Getting started

1. Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone the repo and sync dependencies: `uv sync`
3. Install the Krita plugin (copy to `%APPDATA%\krita\pykrita\` on Windows)
4. Enable plugin in Krita: Settings → Configure Krita → Python Plugin Manager
5. Start Krita with the plugin enabled
6. Run CLI: `uv run krita health`
7. Run MCP server: `uv run python -m krita_mcp.server`

## Development Workflow

### Adding a new tool

1. Define pydantic model in `src/krita_client/models.py`
2. Add HTTP handler in `src/krita_client/client.py`
3. Add CLI subcommand in `src/krita_cli/cli.py`
4. Add MCP tool in `src/krita_mcp/server.py`
5. Add action handler in `krita-plugin/kritamcp/__init__.py`
6. Write tests: unit, integration, property-based
7. Run: `uv run ruff check --fix && uv run ty check && uv run pytest`

### Important: Timeout coordination

If you add a slow operation (export, save, large canvas manipulation):
- Set extended timeout in `krita_client/client.py`
- Ensure the plugin's command queue can handle it (check `get_result()` timeout)
- Both sides must match

## Testing

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# Property-based tests
uv run pytest tests/property/

# E2E tests (requires Krita)
uv run pytest tests/e2e/ -m e2e

# With coverage
uv run pytest --cov=krita_client --cov=krita_mcp --cov=krita_cli --cov-fail-under=95

# Mutation testing
uv run mutmut run
```

## Linting & Type Checking

```bash
# Lint
uv run ruff check src/ tests/

# Auto-fix
uv run ruff check --fix src/ tests/

# Format
uv run ruff format src/ tests/

# Type check
uv run ty check src/ types/
```

## Pre-commit

```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

## Release Process

Releases are automated via `python-semantic-release`:
1. Write conventional commit messages (`feat:`, `fix:`, `chore:`, etc.)
2. Push to `main`
3. CI runs lint, typecheck, tests
4. If all pass, semantic-release bumps version, updates changelog, publishes to PyPI, creates GitHub release

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `style:` — formatting (no code change)
- `refactor:` — code refactoring
- `test:` — adding/updating tests
- `chore:` — maintenance tasks

## Known Gotchas

- **Pixel format**: Krita uses BGRA, not RGBA. Color conversions must account for this
- **Main thread**: All Krita API calls must run on the main thread (handled via QTimer)
- **Command queue**: Commands are queued and processed sequentially
- **HTTP server**: Runs in a background thread in the plugin
- **Dimension limits**: Max canvas is 8192x8192 to prevent OOM
- **Path sanitization**: File paths are validated to prevent traversal attacks
- **No auth**: HTTP server is localhost-only
