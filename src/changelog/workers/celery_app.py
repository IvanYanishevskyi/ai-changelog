import logging

from celery import Celery

from changelog.config import settings

logger = logging.getLogger(__name__)

celery = Celery(
    "changelog",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)


@celery.task(name="changelog.process_push")
def process_push(repo_full_name: str, ref: str, commits: list[dict]) -> dict:
    logger.info("Processing push for %s ref=%s commits=%d", repo_full_name, ref, len(commits))
    return {"status": "processed", "repo": repo_full_name, "commit_count": len(commits)}
