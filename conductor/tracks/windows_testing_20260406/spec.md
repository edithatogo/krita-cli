# Track Specification: Windows Krita Validation & Plugin-Load Reliability

## Problem Statement

The Windows path for Krita MCP is not fully validated end to end. The project has a broken local Python runtime in the validation environment, the plugin files can be copied into `%APPDATA%\krita\pykrita`, and Krita can still fail to expose the HTTP server. That means the failure mode is ambiguous: the plugin may be missing, disabled in Krita's Plugin Manager, failing during import/startup, or simply bound to the wrong port.

Without a dedicated Windows track, the repo cannot reliably distinguish:

1. a broken Python/CLI/MCP environment,
2. a correct install with the plugin disabled,
3. a plugin startup/import failure,
4. or a valid live Krita session where the health endpoint is reachable.

## Requirements

1. **Runtime Preflight** - Add a fast validation step that detects broken native Python dependencies before test collection. The known failure mode is `_ssl` / `_ctypes` import failure in the project venv.
2. **CLI and MCP Validation** - Verify the CLI and MCP packages import and run on a healthy Windows Python runtime.
3. **Plugin Deployment Check** - Verify the Krita plugin files are copied into `%APPDATA%\krita\pykrita\` with the expected `.desktop` file and package layout.
4. **Enablement Diagnostics** - When Krita is running but `/health` is unavailable, report whether the likely issue is plugin disablement, import/startup failure, or a port/config mismatch.
5. **Live Krita Smoke** - Keep a real Windows Krita smoke suite that exercises health, canvas creation, one paint action, and one export/batch path.
6. **Mock E2E Coverage** - Keep the mock server E2E path as the default repo-level fallback so validation still runs without Krita.
7. **Setup Docs** - Document the required Windows workflow: healthy Python runtime, `uv sync`, plugin copy target, Plugin Manager enablement, restart, and health verification.

## Acceptance Criteria

- [ ] A Windows preflight fails early when native Python imports are broken.
- [ ] CLI and MCP tests run on a healthy Windows runtime.
- [ ] The plugin install target and enablement step are documented clearly.
- [ ] Live Krita failures distinguish disablement from startup/import failure.
- [ ] Mock E2E continues to run without a real Krita session.
- [ ] Windows setup guidance explains how to verify `/health` end to end.
