from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from changelog.config import settings
from changelog.db import get_db
from changelog.db.models import User

DASHBOARD_URL = "https://gitlog.space/dashboard"

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class UserOut(BaseModel):
    id: int
    github_id: int
    login: str
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


def create_jwt(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_jwt(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def get_token_from_request(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return request.cookies.get("access_token")


async def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_jwt(token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.get("/login")
async def login() -> RedirectResponse:
    if not settings.github_oauth_client_id:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")
    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.github_oauth_client_id}"
        f"&redirect_uri={settings.github_oauth_redirect_uri}"
        "&scope=read:user+user:email"
    )
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(
    code: str, db: Session = Depends(get_db)
) -> RedirectResponse:
    if not settings.github_oauth_client_id or not settings.github_oauth_client_secret:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.github_oauth_client_id,
                "client_secret": settings.github_oauth_client_secret,
                "code": code,
                "redirect_uri": settings.github_oauth_redirect_uri,
            },
            headers={"Accept": "application/json"},
        )
        token_data: dict[str, Any] = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("OAuth token exchange failed: %s", token_data)
            return RedirectResponse(url=f"{DASHBOARD_URL}?error=auth_failed")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        github_user: dict[str, Any] = user_resp.json()

    github_id = int(github_user["id"])
    user = db.query(User).filter(User.github_id == github_id).first()

    if user:
        user.access_token = access_token
        user.login = github_user.get("login", user.login)
        user.name = github_user.get("name", user.name)
        user.email = github_user.get("email", user.email)
        user.avatar_url = github_user.get("avatar_url", user.avatar_url)
    else:
        user = User(
            github_id=github_id,
            login=github_user.get("login", "unknown"),
            name=github_user.get("name"),
            email=github_user.get("email"),
            avatar_url=github_user.get("avatar_url"),
            access_token=access_token,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    token = create_jwt(user.id)
    redirect = RedirectResponse(url=f"{DASHBOARD_URL}#access_token={token}")
    max_age = settings.jwt_expire_minutes * 60
    redirect.set_cookie(
        key="access_token", value=token, httponly=True,
        max_age=max_age, secure=True, samesite="lax",
    )
    return redirect


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"status": "ok", "message": "Logged out"}
