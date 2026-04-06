# Implementation Plan: Protocol Versioning v2

## Phase 1: Version Infrastructure
- [ ] Task: Define protocol version constants
    - [ ] Write Tests: Unit tests for version comparison and compatibility checks
    - [ ] Implement Feature: Add `PROTOCOL_VERSION = "2.0.0"` constant to client and plugin
- [ ] Task: Add version to health check
    - [ ] Write Tests: Integration test verifying version in health response
    - [ ] Implement Feature: Update plugin `/health` endpoint to include `protocol_version`

## Phase 2: Client & Plugin Version Negotiation
- [ ] Task: Add client version sending and compatibility check
    - [ ] Write Tests: Integration tests for version mismatch scenarios
    - [ ] Implement Feature: Client sends `X-Protocol-Version` header; plugin validates
- [ ] Task: Add feature flags to protocol
    - [ ] Write Tests: Unit tests for feature flag detection
    - [ ] Implement Feature: Plugin reports available features (selection, batch, layers) in health response

## Phase 3: Backward Compatibility
- [ ] Task: Ensure v1 clients work with v2 plugins
    - [ ] Write Tests: Integration test simulating v1 client against v2 plugin
    - [ ] Implement Feature: Plugin accepts requests without version header (treats as v1)
- [ ] Task: Graceful degradation for v2 clients with v1 plugins
    - [ ] Write Tests: Integration test for v2 client detecting v1 plugin
    - [ ] Implement Feature: Client disables unsupported features when connecting to v1 plugin
