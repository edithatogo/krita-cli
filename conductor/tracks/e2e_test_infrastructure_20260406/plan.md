# Implementation Plan: E2E Test Infrastructure

## Phase 1: E2E Test Harness
- [ ] Task: Create E2E test harness with mocked Krita plugin
    - [ ] Write Tests: Verify harness starts mock HTTP server with Krita-like responses
    - [ ] Implement Feature: Create `tests/e2e/conftest.py` with fixtures for mock plugin server

## Phase 2: Core E2E Test Scenarios
- [ ] Task: Write E2E selection tests
    - [ ] Implement Feature: Test selection creation + drawing clipping end-to-end
- [ ] Task: Write E2E batch tests
    - [ ] Implement Feature: Test batch operations with multiple commands sequentially
- [ ] Task: Write E2E history tests
    - [ ] Implement Feature: Test command history population after operations
- [ ] Task: Write E2E CLI-to-plugin tests
    - [ ] Implement Feature: Test CLI commands via subprocess against mock plugin
- [ ] Task: Write E2E MCP-to-plugin tests
    - [ ] Implement Feature: Test MCP tool calls against mock plugin

## Phase 3: CI Integration
- [ ] Task: Add E2E job to CI pipeline
    - [ ] Implement Feature: Add `test-e2e` job to `.github/workflows/ci.yml` that runs E2E tests with mock plugin
