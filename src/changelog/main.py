import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from changelog import __version__
from changelog.config import settings
from changelog.health import router as health_router
from changelog.webhooks.github import router as github_router

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        integrations=[StarletteIntegration(), FastApiIntegration()],
    )

app = FastAPI(title=settings.app_name, version=__version__)
app.include_router(health_router)
app.include_router(github_router)
