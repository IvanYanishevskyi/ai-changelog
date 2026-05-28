from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def process_push(
    repo_full_name: str, ref: str, commits: list[dict[str, Any]]
) -> dict[str, Any]:
    logger.info("Processing push for %s ref=%s commits=%d", repo_full_name, ref, len(commits))
    return {"status": "processed", "repo": repo_full_name, "commit_count": len(commits)}
