# Krita MCP — Product Guidelines

## Prose Style

- **Concise and direct.** Prefer short sentences and clear imperatives.
- **No marketing fluff.** Every word should inform, not persuade. Users are developers and AI agents.
- **Active voice.** "Creates a new canvas" not "A new canvas is created."
- **Consistent terminology.** Use "canvas" (not "document" or "image"), "stroke" (not "line" or "brush stroke"), "MCP tool" (not "function" or "API").
- **CLI output:** Use `rich` for structured, color-coded output. Errors are red, success is green, info is dim.
- **Error messages:** State what failed, why (if known), and how to fix it. Include the error code.

## UX Principles

- **Fail fast, fail clearly.** Validate inputs before making network calls. Return structured errors, never silent failures.
- **Idempotency where possible.** Repeated calls with the same parameters should produce the same result (e.g., `set_color`, `new_canvas`).
- **Explicit over implicit.** Don't guess user intent. Require explicit parameters for destructive actions (`clear`, `delete_layer`).
- **Feedback on every action.** Every command returns a human-readable result. Never return empty JSON or `null`.
- **Respect the user's canvas.** Never modify the canvas without an explicit command. No automatic clears, no implicit state changes.

## MCP Tool Design

- **Tool names:** Prefixed with `krita_` to avoid namespace collisions (e.g., `krita_stroke`, `krita_get_canvas`).
- **Tool descriptions:** One sentence summarizing what the tool does. Include parameter descriptions with ranges, defaults, and examples.
- **Return values:** Human-readable strings. Never return raw JSON to the user. Format structured data as labeled lists.
- **Batch tools:** Return a summary with counts and error details. Don't dump every result unless there are errors.

## CLI Design

- **Subcommand names:** Verbs, lowercase, hyphenated if multi-word (e.g., `new-canvas`, `get-color-at`).
- **Options:** `--long-form` with short `-l` where frequently used.
- **Help text:** Every command and option must have a `help=` string. `--help` should be sufficient to use any command.
- **Exit codes:** 0 for success, 1 for user error (bad input), 2 for connection failure, 130 for Ctrl+C.

## Error Handling

- **Structured errors:** Use `KritaErrorResponse` with code, message, and recoverable flag.
- **Error codes:** Semantic and uppercase (e.g., `NO_ACTIVE_DOCUMENT`, `COMMAND_TIMEOUT`, `PATH_TRAVERSAL_BLOCKED`).
- **Recoverable flag:** `true` if retrying might succeed (timeout, no active layer), `false` if the request itself is invalid (unknown action, traversal attempt).
- **Plugin side:** Log all errors with stack traces. Return clean JSON errors to the client.

## Security

- **No auth needed:** Server binds to `localhost` only. Document this clearly.
- **Path sanitization:** All file paths are validated to prevent directory traversal.
- **Input validation:** Pydantic models validate all parameters before they reach the plugin.
- **Dimension limits:** Max canvas 8192×8192 to prevent OOM. Max 100 layers per document.
- **No secrets:** No API keys, tokens, or credentials are stored or transmitted.

## Documentation

- **README-first:** The README is the single source of truth for getting started.
- **Code examples:** Every tool and CLI command has at least one example in docstrings.
- **Changelog:** Automated via `python-semantic-release`. Conventional commits drive version bumps.
- **Conductor docs:** `conductor/` files describe the project plan, not the product itself.
