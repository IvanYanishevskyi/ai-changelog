import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from changelog import __version__
from changelog.auth import router as auth_router
from changelog.config import settings
from changelog.db import engine
from changelog.db.base import Base
from changelog.health import router as health_router
from changelog.rate_limit import RateLimitMiddleware
from changelog.webhooks.github import router as github_router

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[StarletteIntegration(), FastApiIntegration()],
    )

app = FastAPI(title=settings.app_name, version=__version__)
app.add_middleware(RateLimitMiddleware)
app.include_router(health_router)
app.include_router(github_router)
app.include_router(auth_router)


@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)
