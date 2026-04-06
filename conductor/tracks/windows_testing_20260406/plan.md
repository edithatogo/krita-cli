# Implementation Plan: Windows-Specific Testing

## Phase 1: Windows CI Job
- [ ] Task: Add Windows job to CI workflow
    - [ ] Implement Feature: Add `test-windows` job to `.github/workflows/ci.yml` running on `windows-latest`
- [ ] Task: Fix any Windows-specific test failures
    - [ ] Implement Feature: Patch path handling, file operations, and HTTP server code for Windows compatibility

## Phase 2: Windows-Specific Tests
- [ ] Task: Add Windows path handling tests
    - [ ] Write Tests: Tests for backslash paths, drive letters, UNC paths in save/open/clear commands
    - [ ] Implement Feature: Add `tests/unit/test_windows_paths.py`
- [ ] Task: Add plugin installation tests for Windows
    - [ ] Write Tests: Test plugin copy to `%APPDATA%\krita\pykrita\` path
    - [ ] Implement Feature: Add Windows plugin installation verification script

## Phase 3: Smoke Test Infrastructure
- [ ] Task: Create smoke test that runs without Krita
    - [ ] Write Tests: Smoke test verifying CLI and client work with mock HTTP server
    - [ ] Implement Feature: Add `tests/smoke/test_smoke.py` that runs on all platforms
