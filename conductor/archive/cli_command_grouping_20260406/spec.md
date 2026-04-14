# Track Specification: CLI Command Grouping

## Phase 12: CLI Organization

### Problem Statement

The CLI currently has 30+ flat subcommands. Users must remember exact command names or scan `krita --help` to find what they need. Grouping commands by domain (canvas, brush, selection, file, layer, etc.) would improve discoverability and align with standard CLI design patterns.

### Requirements

1. **Command Groups** — Organize subcommands into logical groups: `krita canvas`, `krita brush`, `krita selection`, `krita file`, `krita layer`, `krita config`, `krita tools`.
2. **Backward Compatibility** — Existing flat commands (`krita stroke`, `krita fill`) continue to work as aliases or deprecation warnings pointing to grouped commands.
3. **Help System** — Each group has its own `--help` with descriptions. Top-level `krita --help` shows groups, not individual commands.
4. **CLI Design** — `krita canvas new`, `krita canvas clear`, `krita canvas info`, `krita brush set`, `krita brush list`, `krita selection rect`, `krita file open`, `krita file save`, etc.

### Acceptance Criteria

- [ ] All 30+ commands organized into 6-8 logical groups
- [ ] Backward-compatible aliases for all existing flat commands
- [ ] Group help text shows available subcommands with descriptions
- [ ] All new code passes lint, type check, and test suites
- [ ] Migration guide documented for existing users/scripts
