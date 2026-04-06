# Implementation Plan: Rollback Mechanisms

## Phase 1: Models & Client
- [x] Task: Add rollback pydantic models and client method
    - [x] Write Tests: Unit tests for `RollbackParams`, `BatchSnapshot`, and `RollbackResponse` models
    - [x] Implement Feature: Add models in `src/krita_client/models.py`; add `rollback` method in `src/krita_client/client.py`
- [x] Task: Conductor - User Manual Verification 'Models & Client' (Protocol in workflow.md)

## Phase 2: Plugin Endpoint
- [x] Task: Add batch snapshot tracking and rollback handler
    - [x] Write Tests: Integration tests for snapshot creation and rollback execution
    - [x] Implement Feature: Add `BatchSnapshotStore` in plugin; modify `cmd_batch` to create snapshots; add `cmd_rollback` handler
- [x] Task: Conductor - User Manual Verification 'Plugin Endpoint' (Protocol in workflow.md)

## Phase 3: CLI & MCP Support
- [x] Task: Add rollback CLI and MCP tools
    - [x] Write Tests: CLI and MCP unit tests for rollback command and tool
    - [x] Implement Feature: Add `krita rollback <batch_id>` CLI subcommand; add `krita_rollback(batch_id: str)` MCP tool
- [x] Task: Conductor - User Manual Verification 'CLI & MCP Support' (Protocol in workflow.md)

## Phase: Review Fixes
- [x] Task: Apply review suggestions aeb7f9c

