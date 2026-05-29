from __future__ import annotations

import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt

from changelog.config import settings

logger = logging.getLogger(__name__)

IAT_CACHE: dict[int, dict[str, Any]] = {}


def create_app_jwt() -> str:
    if not settings.github_app_id or not settings.github_app_private_key:
        raise ValueError("GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY must be set")
    now = datetime.now(UTC)
    payload = {
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "iss": settings.github_app_id,
    }
    token: str = jwt.encode(payload, settings.github_app_private_key, algorithm="RS256")
    return token


async def get_installation_token(installation_id: int) -> str:
    cached = IAT_CACHE.get(installation_id)
    if cached and cached["expires_at"] > time.time() + 120:
        cached_token: str = cached["token"]
        return cached_token
    app_jwt = create_app_jwt()
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
    token: str = data.get("token", "")
    IAT_CACHE[installation_id] = {
        "token": token,
        "expires_at": data.get("expires_at", time.time() + 3600),
    }
    logger.info("Obtained IAT for installation %d", installation_id)
    return token


async def get_installation_repos(
    installation_id: int,
) -> list[dict[str, Any]]:
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    repos: list[dict[str, Any]] = []
    url: str | None = "https://api.github.com/installation/repositories"
    async with httpx.AsyncClient() as client:
        while url:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            repos.extend(data.get("repositories", []))
            url = resp.links.get("next", {}).get("url")
    return repos
