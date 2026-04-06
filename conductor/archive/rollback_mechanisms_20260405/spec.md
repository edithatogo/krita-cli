# Specification: Rollback Mechanisms

## Overview
Add the ability to undo batch operations by tracking execution snapshots and providing a rollback endpoint.

## Scope

### Rollback Endpoint
- New action: `rollback` — undoes a batch of commands by batch ID
- Tracks batch execution snapshots (canvas state before/after)
- Returns `ROLLBACK_NOT_POSSIBLE` if canvas state has changed since batch execution
- Returns `BATCH_NOT_FOUND` if batch ID is invalid

### Batch Snapshot Tracking
- Each batch execution creates a snapshot record with:
  - Unique batch ID (UUID)
  - Commands executed
  - Canvas export path (before batch)
  - Timestamp
- Snapshots stored in memory (configurable max: 50)

### CLI & MCP Support
- CLI: `krita rollback <batch_id>` — triggers rollback
- MCP tool: `krita_rollback(batch_id: str)` — triggers rollback
- Batch responses include the batch ID for later rollback

## Acceptance Criteria
- Rollback endpoint works and returns correct responses
- Batch snapshots are tracked with unique IDs
- CLI and MCP can trigger rollbacks
- Graceful failure when rollback is not possible
- Unit, integration, and E2E tests
- Lint, type check, test suite pass with 95%+ coverage
