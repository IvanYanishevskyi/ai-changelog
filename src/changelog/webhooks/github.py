from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from changelog.config import settings
from changelog.db import SessionLocal
from changelog.db.models import Installation, Repository, WebhookDelivery

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_signature(payload: bytes, signature: str) -> bool:
    if not settings.github_webhook_secret:
        return True
    expected = hmac.new(
        settings.github_webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(default=""),
    x_github_event: str = Header(default=""),
) -> dict[str, Any]:
    payload = await request.body()

    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    event_data: dict[str, Any] = await request.json()
    logger.info("Received GitHub event: %s", x_github_event)

    if x_github_event == "push":
        from changelog.workers.background import process_push

        repo = event_data.get("repository", {}).get("full_name", "unknown")
        ref = event_data.get("ref", "")
        commits = event_data.get("commits", [])
        logger.info("Push event for repo: %s ref=%s commits=%d", repo, ref, len(commits))

        # Upsert repository record so dashboard can find it
        gh_repo = event_data.get("repository", {})
        gh_install_id = event_data.get("installation", {}).get("id")
        db = SessionLocal()
        try:
            # Find the installation this repo belongs to
            install = None
            if gh_install_id:
                install = db.query(Installation).filter(
                    Installation.github_installation_id == gh_install_id
                ).first()

            repo_record = db.query(Repository).filter(
                Repository.github_repo_id == gh_repo.get("id")
            ).first()
            if not repo_record and install:
                repo_record = Repository(
                    github_repo_id=int(gh_repo.get("id") or 0),
                    full_name=gh_repo.get("full_name", repo),
                    default_branch=gh_repo.get("default_branch", "main"),
                    private=gh_repo.get("private", False),
                    installation_id=install.id,
                )
                db.add(repo_record)
                db.commit()
                db.refresh(repo_record)
                logger.info("Created repo %s for installation %s", repo_record.full_name, install.id)
            elif not repo_record:
                logger.warning("Repo %s not found and no installation %s exists", repo, gh_install_id)
            repo_id = repo_record.id if repo_record else None
        finally:
            db.close()

        background_tasks.add_task(_record_delivery, x_github_event, event_data)
        background_tasks.add_task(process_push, repo, ref, commits, repo_id)
        return {"status": "accepted", "event": "push", "repo": repo}

    if x_github_event in ("installation", "installation_repositories"):
        background_tasks.add_task(_record_delivery, x_github_event, event_data)

        gh_installation = event_data.get("installation", {})
        gh_install_id = gh_installation.get("id")
        account = event_data.get("account") or gh_installation.get("account", {})
        repo_sel = event_data.get("repositories_selected") or event_data.get("repositories", [])
        action = event_data.get("action", "created")
        logger.info(
            "Installation event: action=%s install_id=%s account=%s repos=%s",
            action, gh_install_id, account.get("login"), len(repo_sel),
        )
        db = SessionLocal()
        try:
            existing = db.query(Installation).filter(
                Installation.github_installation_id == gh_install_id
            ).first()
            if action == "deleted":
                if existing:
                    db.delete(existing)
            elif existing:
                existing.account_login = account.get("login", existing.account_login)
            else:
                db.add(Installation(
                    github_installation_id=gh_install_id,
                    account_login=account.get("login", "unknown"),
                    account_type=account.get("type", "User"),
                    target_type=event_data.get("target_type", "User"),
                ))
            db.commit()

            # Sync repository list for both installation and installation_repositories events
            install = db.query(Installation).filter(
                Installation.github_installation_id == gh_install_id
            ).first()
            if install:
                if x_github_event == "installation":
                    # Initial install: repo_sel contains all selected repositories
                    for r in repo_sel:
                        existing_repo = db.query(Repository).filter(
                            Repository.github_repo_id == r.get("id")
                        ).first()
                        if existing_repo:
                            existing_repo.installation_id = install.id
                            existing_repo.full_name = r.get("full_name", existing_repo.full_name)
                            existing_repo.private = r.get("private", existing_repo.private)
                            existing_repo.default_branch = r.get("default_branch", existing_repo.default_branch)
                        else:
                            db.add(Repository(
                                github_repo_id=int(r.get("id") or 0),
                                full_name=r.get("full_name", "unknown"),
                                private=r.get("private", False),
                                default_branch=r.get("default_branch", "main"),
                                installation_id=install.id,
                            ))
                elif x_github_event == "installation_repositories":
                    # Handle added repos
                    added = event_data.get("repositories_added", [])
                    for r in added:
                        existing_repo = db.query(Repository).filter(
                            Repository.github_repo_id == r.get("id")
                        ).first()
                        if existing_repo:
                            existing_repo.installation_id = install.id
                            existing_repo.full_name = r.get("full_name", existing_repo.full_name)
                            existing_repo.private = r.get("private", existing_repo.private)
                            existing_repo.default_branch = r.get("default_branch", existing_repo.default_branch)
                        else:
                            db.add(Repository(
                                github_repo_id=int(r.get("id") or 0),
                                full_name=r.get("full_name", "unknown"),
                                private=r.get("private", False),
                                default_branch=r.get("default_branch", "main"),
                                installation_id=install.id,
                            ))
                    # Handle removed repos
                    removed = event_data.get("repositories_removed", [])
                    for r in removed:
                        db.query(Repository).filter(
                            Repository.github_repo_id == int(r.get("id") or 0)
                        ).delete(synchronize_session=False)
                db.commit()
        finally:
            db.close()
        return {"status": "accepted", "event": x_github_event, "action": action}

    background_tasks.add_task(_record_delivery, x_github_event, event_data)
    return {"status": "ignored", "event": x_github_event}


def _record_delivery(event_type: str, event_data: dict[str, Any]) -> None:
    try:
        db = SessionLocal()
        try:
            delivery = WebhookDelivery(
                event_type=event_type,
                action=event_data.get("action"),
                installation_id=(
                    event_data.get("installation", {}).get("id")
                    or event_data.get("installation_id")
                ),
                repo_full_name=event_data.get("repository", {}).get("full_name"),
            )
            db.add(delivery)
            db.commit()
        finally:
            db.close()
    except Exception:
        logger.exception("Failed to record webhook delivery")
