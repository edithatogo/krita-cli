# Track Specification: Windows-Specific Testing

## Phase 12: CI/CD Enhancement

### Problem Statement

The CI runs on Ubuntu only. Path handling, plugin loading, file operations, and HTTP server behavior differ significantly on Windows. Without Windows testing, platform-specific bugs (path separators, file permissions, process management) go undetected until users report them.

### Requirements

1. **Windows CI Job** — Add a Windows CI job that runs the full test suite (unit, integration, property-based) on `windows-latest`.
2. **Path Handling Tests** — Add tests specifically for Windows path handling (backslashes, drive letters, UNC paths).
3. **Plugin Installation Tests** — Verify the Krita plugin installs correctly on Windows (`%APPDATA%\krita\pykrita\`).
4. **HTTP Server Compatibility** — Verify the plugin's HTTP server works correctly on Windows (threading, socket binding).
5. **Smoke Test Mode** — If full Krita is not available on Windows CI runners, at minimum run a smoke test that verifies the client library and CLI work with a mock server.

### Acceptance Criteria

- [ ] Windows CI job runs on every PR
- [ ] All unit and integration tests pass on Windows
- [ ] Path handling tests cover Windows-specific edge cases
- [ ] Plugin installation documented and tested for Windows
- [ ] Smoke test runs even without Krita installed
- [ ] All new code passes lint, type check, and test suites
