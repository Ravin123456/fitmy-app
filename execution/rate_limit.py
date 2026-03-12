"""
FitMY Execution Script: Rate Limiter

Tracks and enforces per-IP and per-user request rate limits.

Module: Security
Directive: directives/security_hardening.md

Default limits:
    Login:        5 attempts / 15 minutes per IP
    API:          60 requests / minute per user
    Registration: 3 accounts / hour per IP
"""

import time
from collections import defaultdict


class RateLimiter:
    """In-memory rate limiter using sliding window counters."""

    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self._windows: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        """
        Check if a key has exceeded its rate limit.

        Args:
            key: Unique identifier (e.g., 'login:192.168.1.1' or 'api:user123').
            max_requests: Maximum requests allowed in the window.
            window_seconds: Time window in seconds.

        Returns:
            True if rate-limited (request should be denied).
        """
        now = time.time()
        cutoff = now - window_seconds

        # Clean old entries
        self._windows[key] = [t for t in self._windows[key] if t > cutoff]

        if len(self._windows[key]) >= max_requests:
            return True

        # Record this request
        self._windows[key].append(now)
        return False

    def get_retry_after(self, key: str, window_seconds: int) -> int:
        """
        Calculate seconds until the rate limit resets.

        Args:
            key: The rate limit key.
            window_seconds: The window size.

        Returns:
            Seconds until the oldest entry expires from the window.
        """
        if not self._windows[key]:
            return 0

        oldest = min(self._windows[key])
        retry_after = int((oldest + window_seconds) - time.time())
        return max(0, retry_after)


# Singleton instance
rate_limiter = RateLimiter()


# Convenience functions
def check_login_rate(ip_address: str) -> bool:
    """Check if login attempts are rate-limited (5/15min per IP)."""
    return rate_limiter.is_rate_limited(f"login:{ip_address}", 5, 900)


def check_api_rate(user_id: str) -> bool:
    """Check if API requests are rate-limited (60/min per user)."""
    return rate_limiter.is_rate_limited(f"api:{user_id}", 60, 60)


def check_registration_rate(ip_address: str) -> bool:
    """Check if registration is rate-limited (3/hour per IP)."""
    return rate_limiter.is_rate_limited(f"register:{ip_address}", 3, 3600)
