from __future__ import annotations

from typing import Any

import redis
from fastapi import APIRouter
from sqlalchemy import text

from changelog.config import settings
from changelog.db import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    status = {"status": "ok", "redis": "unknown", "database": "unknown"}
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "unavailable"
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception:
        status["database"] = "unavailable"
    
    return status


@router.get("/ready")
def readiness_check():
    return {"status": "ready"}
