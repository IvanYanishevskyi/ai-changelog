from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from changelog.auth import get_current_user
from changelog.db import get_db
from changelog.db.models import (
    AudienceMode,
    Changelog,
    ChangelogFormat,
    Installation,
    Repository,
    User,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["dashboard"])


class ChangelogOut(BaseModel):
    id: int
    version: str
    tag: str | None = None
    format: str
    audience: str
    content: str
    commit_count: int = 0
    pr_number: int | None = None
    status: str = "generated"
    generated_at: datetime

    model_config = {"from_attributes": True}


class ChangelogSummary(BaseModel):
    id: int
    version: str
    tag: str | None = None
    format: str
    status: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class RepositoryOut(BaseModel):
    id: int
    github_repo_id: int
    full_name: str
    default_branch: str
    private: bool
    format: str
    audience: str
    created_at: datetime
    updated_at: datetime
    latest_changelog: ChangelogSummary | None = None

    model_config = {"from_attributes": True}


class RepoPatchInput(BaseModel):
    format: str | None = None
    audience: str | None = None


@router.get("/dashboard")
def list_repos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    repos = (
        db.query(Repository)
        .join(Installation)
        .order_by(Repository.full_name)
        .all()
    )
    results: list[dict[str, Any]] = []
    for repo in repos:
        latest = (
            db.query(Changelog)
            .filter(Changelog.repository_id == repo.id)
            .order_by(desc(Changelog.generated_at))
            .first()
        )
        data = {
            "id": repo.id,
            "github_repo_id": repo.github_repo_id,
            "full_name": repo.full_name,
            "default_branch": repo.default_branch,
            "private": repo.private,
            "format": repo.format.value,
            "audience": repo.audience.value,
            "created_at": repo.created_at.isoformat(),
            "updated_at": repo.updated_at.isoformat(),
        }
        if latest:
            data["latest_changelog"] = {
                "id": latest.id,
                "version": latest.version,
                "tag": latest.tag,
                "format": latest.format.value,
                "status": latest.status,
                "generated_at": latest.generated_at.isoformat(),
            }
        results.append(data)
    return results


@router.get("/repos/{repo_id}")
def get_repo(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    latest = (
        db.query(Changelog)
        .filter(Changelog.repository_id == repo.id)
        .order_by(desc(Changelog.generated_at))
        .first()
    )
    data: dict[str, Any] = {
        "id": repo.id,
        "github_repo_id": repo.github_repo_id,
        "full_name": repo.full_name,
        "default_branch": repo.default_branch,
        "private": repo.private,
        "format": repo.format.value,
        "audience": repo.audience.value,
        "created_at": repo.created_at.isoformat(),
        "updated_at": repo.updated_at.isoformat(),
    }
    if latest:
        data["latest_changelog"] = {
            "id": latest.id,
            "version": latest.version,
            "tag": latest.tag,
            "format": latest.format.value,
            "status": latest.status,
            "generated_at": latest.generated_at.isoformat(),
        }
    return data


@router.patch("/repos/{repo_id}")
def update_repo(
    repo_id: int,
    body: RepoPatchInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if body.format is not None:
        try:
            repo.format = ChangelogFormat(body.format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid format: {body.format}")
    if body.audience is not None:
        try:
            repo.audience = AudienceMode(body.audience)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid audience: {body.audience}")
    db.commit()
    db.refresh(repo)
    return {
        "id": repo.id,
        "full_name": repo.full_name,
        "format": repo.format.value,
        "audience": repo.audience.value,
        "updated_at": repo.updated_at.isoformat(),
    }


@router.get("/repos/{repo_id}/changelogs")
def list_changelogs(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    total = (
        db.query(Changelog)
        .filter(Changelog.repository_id == repo_id)
        .count()
    )
    changelogs = (
        db.query(Changelog)
        .filter(Changelog.repository_id == repo_id)
        .order_by(desc(Changelog.generated_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [
            {
                "id": c.id,
                "version": c.version,
                "tag": c.tag,
                "format": c.format.value,
                "audience": c.audience.value,
                "status": c.status,
                "commit_count": c.commit_count,
                "pr_number": c.pr_number,
                "generated_at": c.generated_at.isoformat(),
            }
            for c in changelogs
        ],
    }


@router.get("/changelogs/{changelog_id}")
def get_changelog(
    changelog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    changelog = db.query(Changelog).filter(Changelog.id == changelog_id).first()
    if not changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")
    return {
        "id": changelog.id,
        "version": changelog.version,
        "tag": changelog.tag,
        "format": changelog.format.value,
        "audience": changelog.audience.value,
        "content": changelog.content,
        "commit_count": changelog.commit_count,
        "pr_number": changelog.pr_number,
        "status": changelog.status,
        "generated_at": changelog.generated_at.isoformat(),
        "repository": {
            "id": changelog.repository.id,
            "full_name": changelog.repository.full_name,
        },
    }


@router.post("/changelogs/{changelog_id}/regenerate")
def regenerate_changelog(
    changelog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    changelog = db.query(Changelog).filter(Changelog.id == changelog_id).first()
    if not changelog:
        raise HTTPException(status_code=404, detail="Changelog not found")
    return {
        "status": "queued",
        "message": f"Re-generation queued for changelog {changelog_id}",
    }


@router.get("/install/callback")
def install_callback(
    request: Request,
    installation_id: int | None = None,
    setup_action: str | None = None,
) -> dict[str, Any]:
    logger.info(
        "Install callback: installation_id=%s setup_action=%s",
        installation_id,
        setup_action,
    )
    return {
        "status": "success",
        "message": "GitHub App installed successfully",
        "installation_id": installation_id,
        "setup_action": setup_action,
    }
