# Specification: Command History & Replay

## Overview
Add command execution history logging and the ability to replay recorded commands.

## Scope

### Command History Log
- In-memory history store in plugin (last 100 commands, configurable)
- Records: action, params (sanitized), timestamp, result status, duration
- New endpoint: `get_command_history` — returns history as JSON
- New error code: `HISTORY_DISABLED` if history is turned off

### CLI History Command
- `krita history [--limit N] [--json]` — queries and displays history
- Default: shows last 20 commands in human-readable format
- `--json`: outputs raw JSON for scripting

### MCP History Tool
- `krita_get_command_history(limit: int = 20)` — returns history as formatted string

### Replay CLI
- `krita replay <file.json>` — replays commands from a JSON file
- `--speed 1.0x` — controls delay between commands (0.0 = instant, 1.0 = original timing)
- `--dry-run` — validates commands without executing
- Integrates with history export: `krita history --json > replay.json` then `krita replay replay.json`

## Acceptance Criteria
- History records all successful commands with metadata
- History queryable via CLI, MCP, and direct HTTP
- Replay executes commands correctly with speed control
- Dry-run mode validates without side effects
- All features have unit, integration, and E2E tests
- Lint, type check, test suite pass with 95%+ coverage
