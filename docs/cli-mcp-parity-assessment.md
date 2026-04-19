# CLI vs MCP Parity Assessment

Short answer: yes, the MCP server should be brought to parity with the stable, agent-useful CLI surface. No, it should not blindly mirror every helper or every plugin action name.

## What Changed

The repo now closes the obvious low-risk MCP parity gaps by adding wrappers for:

- Layer operations
- `select_area` as the same compatibility alias used by the CLI
- `delete_selection_channel`
- `combine_selections` with a real mask-backed second selection source
- CLI `get_capabilities`

It also fixes a real mismatch in the plugin dispatch table by wiring:

- `select_by_color`
- `select_by_alpha`

That means the declared client, CLI, and MCP surfaces for those two operations are now backed by real plugin dispatch entries instead of dead declarations.

## Current Position

After those changes:

- The plugin-backed baseline is `52` actions
- The CLI covers `52/52`
- The MCP server covers `52/52`

There is no remaining plugin-backed action gap between the CLI and MCP surfaces.

## Why `combine_selections` Needed Real Semantics

`combine_selections` was not just "missing plumbing." The earlier plugin implementation said:

- it is a placeholder
- it does not take a real second selection source
- it only records an operation mode for a later step

That was not solid enough for an agent-facing CLI or MCP tool. The implementation now combines:

- the active selection already present in the document
- a second selection loaded from a mask file supplied as `mask_path`

That keeps the intent explicit and gives the command a concrete, testable second operand.

## What Counts As Real Parity

For this project, parity should mean:

- the same stable user intents are available in both CLI and MCP
- the wrapper is backed by a real plugin action, not a dead declaration
- aliases stay aliases where that keeps the public surface simpler

Parity should not mean:

- duplicating local CLI helpers like `config`, `replay`, or `call`
- exposing placeholder plugin actions just because they have a name
- forcing identical naming when one side is intentionally a compatibility alias

## Recommendation

Treat MCP parity as a selective goal:

1. Keep MCP aligned with the stable plugin-backed CLI surface.
2. Prefer explicit operand sources over implicit mode-setting placeholders.
3. Use the inventory and coverage matrix docs to prevent declared-but-undispatched regressions.

In practice, that means the CLI and MCP server are now aligned for the stable, agent-useful surface. The remaining work is broader API strategy rather than parity cleanup.
