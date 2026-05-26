import redis
from fastapi import APIRouter

from changelog.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    status = {"status": "ok", "redis": "unknown"}
    try:
        r = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "unavailable"
    return status


@router.get("/ready")
def readiness_check():
    return {"status": "ready"}
