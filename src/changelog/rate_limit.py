from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens: dict[str, float] = defaultdict(float)
        self.last_refill: dict[str, float] = defaultdict(float)

    def consume(self, key: str, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill[key]
        self.tokens[key] = min(self.capacity, self.tokens[key] + elapsed * self.refill_rate)
        self.last_refill[key] = now

        if self.tokens[key] >= tokens:
            self.tokens[key] -= tokens
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp,
        ip_bucket: TokenBucket | None = None,
        user_bucket: TokenBucket | None = None,
    ) -> None:
        super().__init__(app)
        self.ip_bucket = ip_bucket or TokenBucket(capacity=60, refill_rate=1.0)
        self.user_bucket = user_bucket or TokenBucket(capacity=200, refill_rate=5.0)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        client_ip = request.client.host if request.client else "unknown"
        if not self.ip_bucket.consume(client_ip):
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})

        user_id = getattr(request.state, "user_id", None)
        if user_id and not self.user_bucket.consume(str(user_id)):
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})

        response = await call_next(request)
        return response
