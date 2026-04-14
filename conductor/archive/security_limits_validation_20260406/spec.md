# Track Specification: Security & Limits Validation

## Phase 11b: Security & Limits Validation

### Problem Statement

The current system has basic path sanitization and dimension limits, but lacks comprehensive security controls. Without proper rate limiting, request size validation, and resource quotas, the system is vulnerable to abuse (intentional or accidental) from AI agents or automated scripts sending excessive requests.

### Requirements

1. **Rate Limiting** — Token bucket rate limiter on the plugin HTTP server. Configurable requests-per-second and burst size.
2. **Request Size Limits** — Validate and reject requests exceeding max payload size (prevent OOM from massive point arrays).
3. **Command Quota System** — Track total commands per session; configurable hard limits.
4. **Canvas Dimension Validation** — Enforce max canvas size at creation time (already partially implemented, needs hardening).
5. **File Path Validation** — Comprehensive path traversal prevention for save/open operations.
6. **Memory Limits** — Monitor and cap memory usage for batch operations and snapshot storage.
7. **Security Error Codes** — Standardized error responses for all security violations (`RATE_LIMITED`, `PAYLOAD_TOO_LARGE`, `QUOTA_EXCEEDED`, `PATH_TRAVERSAL`, `MEMORY_LIMIT`).
8. **Configuration** — All limits configurable via plugin settings with sensible defaults.

### Acceptance Criteria

- [ ] Rate limiter rejects requests exceeding threshold with proper error code
- [ ] Payload size limits enforced on all endpoints
- [ ] Command quota system tracks and enforces limits
- [ ] Canvas dimension validation is comprehensive and tested
- [ ] Path traversal attempts are blocked and logged
- [ ] Memory limits prevent OOM during batch operations
- [ ] All security errors return standardized error codes
- [ ] Property-based tests cover edge cases for all validators
- [ ] Configuration exposed via CLI and plugin settings
- [ ] All new code passes lint, type check, and test suites
