"""Sliding window rate limiter for command execution.

This module is kept separate from the Krita plugin so it can be
imported and tested independently without the Krita runtime.
"""

from __future__ import annotations

import threading
import time


class RateLimiter:
    """Sliding window rate limiter for command execution.

    Tracks timestamps of command executions and rejects requests
    that exceed the configured rate limit within any sliding window.

    SECURITY: Prevents command flooding attacks by limiting the number
    of commands that can be executed within a configurable time window.
    """

    def __init__(self, max_commands: int = 60, window_seconds: float = 60.0) -> None:
        self._max_commands = max_commands
        self._window = window_seconds
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def allow(self) -> bool:
        """Check if a command is allowed under the current rate limit.

        Returns True if the command is allowed (and records the timestamp),
        False if the rate limit is exceeded.
        """
        now = time.monotonic()
        with self._lock:
            # Remove timestamps outside the sliding window
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
