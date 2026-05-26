from __future__ import annotations

from typing import Any

import redis
from fastapi import APIRouter

from changelog.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, Any]:
    status: dict[str, Any] = {"status": "ok", "redis": "unknown"}
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)  # type: ignore[no-untyped-call]
        r.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "unavailable"
    return status


@router.get("/ready")
def readiness_check() -> dict[str, str]:
    return {"status": "ready"}
