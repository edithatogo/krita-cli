"""Unit tests for rate limiter and security config."""

from __future__ import annotations

import threading
import time


class RateLimiter:
    """Sliding window rate limiter — copied from plugin for isolated testing."""

    def __init__(self, max_commands: int = 60, window_seconds: float = 60.0) -> None:
        self._max_commands = max_commands
        self._window = window_seconds
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self._lock:
            cutoff = now - self._window
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self._max_commands:
                return False
            self._timestamps.append(now)
            return True

    @property
    def max_commands(self) -> int:
        return self._max_commands

    @max_commands.setter
    def max_commands(self, value: int) -> None:
        self._max_commands = value


class TestRateLimiter:
    """Tests for the sliding window rate limiter."""

    def test_rate_limiter_allows_under_limit(self) -> None:
        limiter = RateLimiter(max_commands=5, window_seconds=1.0)
        for _ in range(5):
            assert limiter.allow() is True

    def test_rate_limiter_rejects_over_limit(self) -> None:
        limiter = RateLimiter(max_commands=3, window_seconds=1.0)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False

    def test_rate_limiter_resets_after_window(self) -> None:
        limiter = RateLimiter(max_commands=2, window_seconds=0.1)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False
        time.sleep(0.15)
        assert limiter.allow() is True

    def test_rate_limiter_sliding_window(self) -> None:
        limiter = RateLimiter(max_commands=3, window_seconds=0.1)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False
        # Wait for all timestamps to expire from window
        time.sleep(0.15)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False

    def test_rate_limiter_default_config(self) -> None:
        limiter = RateLimiter()
        assert limiter.max_commands == 60

    def test_rate_limiter_configurable(self) -> None:
        limiter = RateLimiter(max_commands=10)
        assert limiter.max_commands == 10
        limiter.max_commands = 20
        assert limiter.max_commands == 20

    def test_rate_limiter_thread_safety(self) -> None:
        limiter = RateLimiter(max_commands=100, window_seconds=1.0)
        allowed: list[int] = []
        lock = threading.Lock()

        def try_allow() -> None:
            for _ in range(20):
                if limiter.allow():
                    with lock:
                        allowed.append(1)

        threads = [threading.Thread(target=try_allow) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(allowed) == 100


class TestClientConfigSecurityLimits:
    """Tests for the client security config."""

    def test_default_security_limits(self) -> None:
        from krita_client.config import ClientConfig

        config = ClientConfig()
        assert config.max_commands_per_minute == 60
        assert config.max_batch_size == 50
        assert config.max_layers == 100


class TestErrorCodeAdditions:
    """Tests for new security error codes."""

    def test_rate_limit_exceeded_code(self) -> None:
        from krita_client.models import ErrorCode

        assert ErrorCode.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"
        assert ErrorCode.BATCH_SIZE_EXCEEDED == "BATCH_SIZE_EXCEEDED"
        assert ErrorCode.LAYER_LIMIT_EXCEEDED == "LAYER_LIMIT_EXCEEDED"
