# Implementation Plan: Command History & Replay

## Phase 1: History Storage & Endpoint
- [x] Task: Add history models and in-memory store `6baa040`
    - [x] Write Tests: Unit tests for `CommandHistoryRecord` model and history store (add, query, eviction)
    - [x] Implement Feature: Add `CommandHistoryRecord` model; add thread-safe history store with configurable max size and LRU eviction in plugin
- [x] Task: Record commands and add history endpoint `6baa040`
    - [x] Write Tests: Integration tests for history recording and `get_command_history` endpoint
    - [x] Implement Feature: Hook into `execute_command` to record each command; add `cmd_get_command_history` handler in plugin
- [x] Task: Conductor - User Manual Verification 'History Storage & Endpoint' (Protocol in workflow.md)
    - [x] Verified: All implementation files exist and tests pass (17/17)
    - [x] Verified: History store thread-safe with LRU eviction, endpoint returns correct format
    - [x] Fixed: Duplicate CLI history system removed; single plugin-side source of truth

## Phase 2: Client, CLI & MCP Support
- [x] Task: Add client method and CLI/MCP tools `6baa040`
    - [x] Write Tests: Integration test for `get_command_history` client method; unit tests for CLI and MCP
    - [x] Implement Feature: Add `get_command_history` in client; add `krita history` CLI subcommand; add `krita_get_command_history` MCP tool
- [x] Task: Conductor - User Manual Verification 'Client, CLI & MCP Support' (Protocol in workflow.md)
    - [x] Verified: CLI `history` command queries plugin endpoint correctly
    - [x] Verified: MCP tool formats history as human-readable string
    - [x] Fixed: Added MCP tool unit tests (3 new tests)

## Phase 3: Replay CLI
- [x] Task: Add replay command module `7c19ac9`
    - [x] Write Tests: Unit tests for replay parsing, validation, speed control, and dry-run mode
    - [x] Implement Feature: Add `krita replay <file>` command with `--speed` and `--dry-run` options in `src/krita_cli/commands/replay.py`
- [x] Task: Integrate replay with history export `7c19ac9`
    - [x] Write Tests: Integration test for history-to-replay pipeline
    - [x] Implement Feature: Ensure `krita history --json` outputs replay-compatible format
- [x] Task: Conductor - User Manual Verification 'Replay CLI' (Protocol in workflow.md)
    - [x] Verified: Replay command validates JSON, supports speed control and dry-run
    - [x] Verified: `krita history --json` output is replay-compatible (array of command records)
