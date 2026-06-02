import time
from collections import deque, defaultdict
from typing import Deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter per IP.

    Not suitable for multi-process or multi-host deployments; replace with
    Redis-backed limiter (e.g., slowapi) for production.
    """

    def __init__(self, app, requests: int | None = None, window_seconds: int | None = None):
        super().__init__(app)
        self.requests = requests or settings.RATE_LIMIT_REQUESTS
        self.window = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self.storage: dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Use client host as the key
        client = request.client.host if request.client else "unknown"
        now = time.time()
        q = self.storage[client]

        # prune old timestamps
        while q and q[0] <= now - self.window:
            q.popleft()

        if len(q) >= self.requests:
            # rate limit exceeded
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        q.append(now)
        response = await call_next(request)
        return response
