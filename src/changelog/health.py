from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from changelog.db import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    status: dict[str, str] = {"status": "ok", "database": "unknown"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception:
        status["database"] = "unavailable"
    return status


@router.get("/ready")
def readiness_check() -> dict[str, str]:
    return {"status": "ready"}
