from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status

from ..config import settings


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self.lock:
            entries = self.requests[key]
            while entries and entries[0] < cutoff:
                entries.popleft()
            if len(entries) >= self.limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please retry later.",
                )
            entries.append(now)

    def reset(self) -> None:
        with self.lock:
            self.requests.clear()


rate_limiter = InMemoryRateLimiter(settings.rate_limit_per_minute)


def enforce_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    rate_limiter.check(client_host)
