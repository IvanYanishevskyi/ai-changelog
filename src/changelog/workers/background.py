from __future__ import annotations

import logging
from typing import Any

from changelog.config import settings
from changelog.llm.formatter import format_changelog
from changelog.llm.provider import get_provider

logger = logging.getLogger(__name__)


def extract_version_from_ref(ref: str) -> str:
    prefix = "refs/tags/"
    if ref.startswith(prefix):
        return ref[len(prefix):]
    return "v0.0.0"


async def process_push(
    repo_full_name: str, ref: str, commits: list[dict[str, Any]]
) -> dict[str, Any]:
    logger.info(
        "Processing push for %s ref=%s commits=%d", repo_full_name, ref, len(commits)
    )
    if not commits:
        return {"status": "skipped", "reason": "no commits", "repo": repo_full_name}

    version = extract_version_from_ref(ref)
    messages = [c.get("message", "") for c in commits]

    provider = get_provider(
        settings.llm_provider,
        api_key=settings.openrouter_api_key,
        model=settings.llm_model,
        base_url=settings.openrouter_base_url,
    )

    classifications: list[dict[str, Any]] = []
    for msg in messages:
        try:
            result = await provider.classify_commit(msg)
            result["message"] = msg
            classifications.append(result)
            logger.info("Classified: %s -> %s", msg[:50], result.get("type", "unknown"))
        except Exception as e:
            logger.error("Classification failed for commit %s: %s", msg[:50], e)
            classifications.append({
                "type": "chore", "summary": msg.split("\n")[0][:80],
                "is_breaking_change": False, "message": msg,
            })

    changelog = format_changelog(
        version=version,
        classifications=classifications,
        fmt="keep_a_changelog",
        repo_url=f"https://github.com/{repo_full_name}",
    )

    logger.info(
        "Changelog generated for %s@%s:\n%s", repo_full_name, version, changelog
    )
    return {
        "status": "generated",
        "repo": repo_full_name,
        "version": version,
        "commit_count": len(commits),
        "classifications": classifications,
        "changelog": changelog,
    }
