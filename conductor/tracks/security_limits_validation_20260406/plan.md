# Implementation Plan: Security & Limits Validation

## Phase 1: Core Security Infrastructure
- [ ] Task: Implement Token Bucket Rate Limiter
    - [ ] Write Tests: Unit tests for rate limiter (token consumption, refill, burst handling)
    - [ ] Implement Feature: Create `RateLimiter` class in `krita-plugin/kritamcp/rate_limiter.py`
- [ ] Task: Define Security Error Code Models
    - [ ] Write Tests: Unit tests for security error response models
    - [ ] Implement Feature: Add `SecurityError` enum and response models in `src/krita_client/models.py`
- [ ] Task: Implement Payload Size Validator
    - [ ] Write Tests: Property-based tests for payload validation edge cases
    - [ ] Implement Feature: Add payload size validation middleware in plugin HTTP handler

## Phase 2: Plugin Security Hardening
- [ ] Task: Command Quota System
    - [ ] Write Tests: Unit tests for quota tracking and enforcement
    - [ ] Implement Feature: Add session-based command quota tracking in `krita-plugin/kritamcp/__init__.py`
- [ ] Task: Enhanced Path Validation
    - [ ] Write Tests: Unit tests for path traversal attack prevention
    - [ ] Implement Feature: Comprehensive path sanitization utility with allowlist validation
- [ ] Task: Memory Limit Enforcement
    - [ ] Write Tests: Unit tests for memory tracking during batch operations
    - [ ] Implement Feature: Memory monitor with soft/hard limits for snapshot store and batch processing

## Phase 3: CLI Config & Integration
- [ ] Task: Security Configuration CLI
    - [ ] Write Tests: Unit tests for config parsing and validation
    - [ ] Implement Feature: Add `krita config security` subcommand to view/set security limits
- [ ] Task: MCP Security Tools
    - [ ] Write Tests: Unit tests for security status MCP tools
    - [ ] Implement Feature: Add `krita_security_status` MCP tool to query current limits and usage
- [ ] Task: Integration & E2E Tests
    - [ ] Write Tests: E2E tests verifying rate limiting, quota enforcement, and path validation end-to-end
    - [ ] Implement Feature: Full integration test suite for all security features
