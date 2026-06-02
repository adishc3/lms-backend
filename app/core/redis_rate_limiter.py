from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.core.config import settings
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = settings.RATE_LIMIT_REQUESTS
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS
        self.redis = None
        self._counters = {}
        # try to initialize redis client if URL provided
        if getattr(settings, "REDIS_URL", None):
            try:
                import redis as _redis

                self.redis = _redis.from_url(settings.REDIS_URL)
                # test connection
                self.redis.ping()
            except Exception:
                self.redis = None

    async def dispatch(self, request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        key = f"rate:{client_host}"

        # try redis first
        if self.redis:
            try:
                count = self.redis.incr(key)
                if count == 1:
                    self.redis.expire(key, self.window)
                if count > self.requests:
                    return Response(status_code=429, content="Too many requests")
            except Exception:
                # fallback to memory
                self.redis = None

        if not self.redis:
            now = int(time.time())
            entry = self._counters.get(key)
            if not entry or now > entry[1]:
                # reset window
                self._counters[key] = [1, now + self.window]
            else:
                entry[0] += 1
                if entry[0] > self.requests:
                    return Response(status_code=429, content="Too many requests")

        response = await call_next(request)
        return response
