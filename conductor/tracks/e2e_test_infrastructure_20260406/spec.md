# Track Specification: E2E Test Infrastructure

## Phase 12: Testing Infrastructure

### Problem Statement

The `tests/e2e/` directory is essentially empty across the entire project. Without E2E tests, we cannot verify that the plugin, client, CLI, and MCP server work together end-to-end. Every feature (selection, batch, history, layers) has been tested in isolation but never as an integrated system.

### Requirements

1. **E2E Test Harness** — Create a test harness that starts the Krita plugin in a headless mode (or mocks the Krita runtime) and runs full end-to-end tests against the complete stack.
2. **E2E Selection Tests** — Verify that creating a selection and then drawing clips correctly end-to-end.
3. **E2E Batch Tests** — Verify batch operations with multiple commands execute sequentially and return correct results.
4. **E2E History Tests** — Verify command history is populated after E2E operations.
5. **E2E CLI-to-Plugin Tests** — Verify CLI commands reach the plugin and return correct responses.
6. **E2E MCP-to-Plugin Tests** — Verify MCP tool calls reach the plugin and return human-readable responses.
7. **CI Integration** — E2E tests run in CI (skipped if Krita unavailable, but at minimum run with mocked plugin).

### Acceptance Criteria

- [ ] E2E test harness supports real Krita and mocked plugin modes
- [ ] At least 5 E2E test scenarios covering full stack
- [ ] E2E tests run in CI pipeline
- [ ] All new code passes lint, type check, and test suites
