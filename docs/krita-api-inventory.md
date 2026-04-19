# Krita API Inventory

Short answer: yes, it is worth mapping the Krita API, but as an inventory and decision aid rather than as a blanket wrapping backlog.

## Why Inventory Matters

For this repo, a full inventory is useful because it gives us three things:

1. A stable reference for what Krita and our local stubs appear to expose.
2. A fast way to spot mismatches between the plugin dispatch table, the typed client, the CLI, and the MCP server.
3. A way to judge wrapper candidates based on actual API surface instead of memory or ad hoc browsing.

That is materially different from saying "wrap everything." Most of Krita's raw Python surface is not automatically a good CLI or MCP tool candidate.

## What To Inventory

There are three relevant layers in this repository:

1. The local stub surface in `types/krita/__init__.pyi`
2. The live Krita runtime surface, when the script is run inside Krita's embedded Python
3. The repo's wrapped surfaces:
   - plugin dispatch actions in `krita-plugin/kritamcp/__init__.py`
   - typed client methods in `src/krita_client/client.py`
   - CLI commands in `src/krita_cli/commands/`
   - MCP tools in `src/krita_mcp/server.py`

The inventory should be the reference. The wrapper layers should be curated projections of that reference.

## Included Script

Use [scripts/export_krita_api_inventory.py](/C:/Users/60217257/repos/krita-cli/krita-mcp/scripts/export_krita_api_inventory.py) to export a repeatable JSON inventory.

It supports:

- `--source stubs`: parse the local `types/krita/__init__.pyi`
- `--source runtime`: inspect a live `krita` module and active objects
- `--source both`: include both in one artifact

Examples:

```bash
python scripts/export_krita_api_inventory.py --source stubs
python scripts/export_krita_api_inventory.py --source both --output docs/generated/krita-api-inventory.json
```

Notes:

- `--source stubs` works in a normal dev shell.
- `--source runtime` requires running inside Krita's Python environment where `import krita` succeeds.
- The runtime export inspects the module, major classes, and the active `Krita`, `Window`, `Document`, `View`, and `Node` objects when available.

## Wrapper Criteria

A raw Krita API should usually become a CLI or MCP tool only if it is:

- A stable user intent rather than a low-level object mutation detail
- Serializable through simple JSON-compatible primitives
- Safe enough for agent use without handing back opaque Qt object graphs
- Testable with mocks and, ideally, live coverage
- Distinct enough to justify a first-class tool instead of an alias

That usually favors actions like layer management, selection transforms, or export operations.

That usually disfavors:

- UI-only hooks and widget interactions
- Methods that return opaque Qt or Krita objects
- Redundant aliases over an existing well-named command
- Placeholder semantics that do not yet perform the advertised operation

## Recommendation

Maintain a complete inventory. Do not maintain a complete wrapper backlog.

The right pattern for this repo is:

1. Keep the inventory broad.
2. Keep the wrapper layers narrow and intentional.
3. Use parity reports to identify real holes and misleading declarations.
4. Promote new APIs into the client, CLI, and MCP only when they clear the wrapper criteria above.
