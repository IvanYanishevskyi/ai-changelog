import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from changelog.config import settings

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
    x_hub_signature_256: str = Header(default=""),
    x_github_event: str = Header(default=""),
):
    payload = await request.body()

    if not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    event_data = await request.json()
    logger.info("Received GitHub event: %s", x_github_event)

    if x_github_event == "push":
        repo = event_data.get("repository", {}).get("full_name", "unknown")
        logger.info("Push event for repo: %s", repo)
        return {"status": "accepted", "event": "push", "repo": repo}

    return {"status": "ignored", "event": x_github_event}
