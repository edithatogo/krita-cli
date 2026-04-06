# Python Code Style Guide — Krita MCP

## Formatting

- **Tool:** `ruff format` (Black-compatible)
- **Line length:** 88 characters (Black default)
- **Quotes:** Double quotes for strings, single quotes only when necessary
- **Trailing commas:** Always add trailing commas in multi-line structures

## Linting

- **Tool:** `ruff check --select ALL` (strict mode)
- **Key rules:**
  - Type hints required on all function signatures
  - No unused imports
  - No bare `except:` clauses
  - Docstrings required on all public modules, classes, and functions
  - Max function length: 50 lines
  - Max complexity: 10

## Type Checking

- **Tool:** `ty check` (Astral's type checker)
- **Coverage:** 100% required on `src/` and `types/`
- **No `Any`:** Avoid `Any` except when interfacing with untyped Krita APIs
- **Use `TYPE_CHECKING`** guards for import-time-only dependencies

## Testing

- **Framework:** `pytest` with `pytest-xdist` for parallel execution
- **Coverage:** 95% minimum enforced
- **Naming:** `test_<function_or_method>_<scenario>.py`
- **Structure:** Arrange-Act-Assert pattern
- **Fixtures:** Use fixtures for shared setup, keep them minimal
- **Mocking:** Prefer `pytest-httpx` for HTTP mocking over manual mocks

## Naming Conventions

- **Modules:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/methods:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private members:** Prefix with single underscore `_private`
- **Pydantic models:** `PascalCase` + "Params" suffix for command parameter models

## Import Order

1. Standard library
2. Third-party (pydantic, httpx, typer, etc.)
3. Local application imports

Use `ruff` to enforce import sorting (`I001`).

## Docstrings

- **Style:** Google docstring format
- **Content:** One-line summary, then Args/Returns/Raises sections
- **CLI help:** Use `typer.Argument(..., help="...")` and `typer.Option(..., help="...")` for CLI documentation

## Git Commits

- **Format:** Conventional Commits (`feat:`, `fix:`, `test:`, `chore:`, `docs:`, `refactor:`)
- **Scope:** One logical change per commit
- **Pre-commit:** `pre-commit run --all-files` before every push
