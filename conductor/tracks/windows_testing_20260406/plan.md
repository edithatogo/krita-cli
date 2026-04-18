# Implementation Plan: Windows Krita Validation & Plugin-Load Reliability

## Phase 1: Runtime Preflight
- Detect broken Windows Python runtimes before collection by importing native modules that fail in the current venv (`ssl`, `ctypes`).
- Add a stdlib-only setup sanity check (`scripts/windows_preflight.py`) that explains how to repair the environment when the local interpreter is broken.
- Keep the preflight separate from the main test suite so the failure mode is obvious.

## Phase 2: CLI and MCP Validation
- Verify the CLI imports and runs on a healthy Windows Python runtime.
- Verify the MCP client/server packages import cleanly on the same runtime.
- Keep the mock E2E suite as the default fallback for repo validation.

## Phase 3: Plugin Deployment and Enablement Diagnostics
- Verify the Krita plugin is copied into `%APPDATA%\krita\pykrita\` with both the `.desktop` file and the `kritamcp/` package.
- Surface a clear message when Krita is running but `/health` never appears.
- Distinguish between:
  - plugin files missing or copied to the wrong location,
  - plugin present but not enabled in Krita's Python Plugin Manager,
  - plugin loaded but failing during import/startup,
  - or a config/port mismatch.

## Phase 4: Live Krita Smoke Validation
- Keep a live Krita driver for Windows that launches Krita, opens a canvas, and waits for the HTTP health endpoint.
- Exercise a minimal live smoke path: health, new canvas, one paint action, and one export or batch action.
- Capture the existing startup log and diagnostic script outputs as the canonical troubleshooting path.

## Phase 5: Documentation and Registry Updates
- Update the Windows setup guide so the required workflow is explicit:
  - healthy Python runtime,
  - `uv sync`,
  - copy plugin files,
  - enable `Krita MCP Bridge`,
  - restart Krita,
  - verify `/health`.
- Keep `krita-mcp/conductor/tracks.md` and the parent Conductor index pointed at this track so future debugging stays in one place.
