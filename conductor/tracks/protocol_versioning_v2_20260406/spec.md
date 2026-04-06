# Track Specification: Protocol Versioning v2

## Phase 12: Protocol Infrastructure

### Problem Statement

The spec mentions protocol versioning but there's no explicit version negotiation between client and plugin. When the plugin is updated with new features (like selection tools) but the client isn't, commands may fail silently or return unexpected results. A version negotiation system would prevent these mismatches.

### Requirements

1. **Protocol Version in Health Check** — The `/health` endpoint returns the plugin's protocol version. The client checks compatibility before executing commands.
2. **Client Protocol Version** — The client sends its protocol version with every request. The plugin rejects requests from incompatible versions.
3. **Version Negotiation** — If versions mismatch, the response includes the plugin's supported version range and a recommendation to update.
4. **Feature Flags** — Instead of breaking changes for new features, use feature flags in the protocol. The plugin reports which features are available (selection, batch, layers, etc.).
5. **Backward Compatibility** — v1 clients continue to work with v2 plugins. V2 clients detect v1 plugins and disable unsupported features gracefully.

### Acceptance Criteria

- [ ] Protocol version included in health check response
- [ ] Client sends protocol version with requests
- [ ] Plugin rejects incompatible versions with clear error message
- [ ] Feature flags reported by plugin for available capabilities
- [ ] Backward compatibility verified: v1 clients work with v2 plugins
- [ ] All new code passes lint, type check, and test suites
