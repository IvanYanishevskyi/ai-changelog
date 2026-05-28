from __future__ import annotations

from datetime import date
from typing import Any

TYPE_LABELS: dict[str, str] = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "perf": "Performance",
    "refactor": "Changed",
    "chore": "Maintenance",
    "test": "Testing",
    "style": "Style",
    "breaking": "Breaking Changes",
}

CONVENTIONAL_EMOJIS: dict[str, str] = {
    "feat": ":sparkles:",
    "fix": ":bug:",
    "docs": ":memo:",
    "perf": ":zap:",
    "refactor": ":recycle:",
    "chore": ":wrench:",
    "test": ":white_check_mark:",
    "style": ":art:",
    "breaking": ":warning:",
}

TYPE_ORDER = ["breaking", "feat", "fix", "perf", "refactor", "docs", "test", "chore", "style"]


def group_by_type(classifications: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for c in classifications:
        t = c.get("type", "chore")
        if t not in groups:
            groups[t] = []
        groups[t].append(c)
    return groups


def format_keep_a_changelog(
    version: str,
    groups: dict[str, list[dict[str, Any]]],
    repo_url: str = "",
    date_str: str | None = None,
) -> str:
    if date_str is None:
        date_str = date.today().isoformat()
    lines: list[str] = [
        f"## [{version}] - {date_str}",
        "",
    ]
    for t in TYPE_ORDER:
        if t not in groups:
            continue
        label = TYPE_LABELS.get(t, t.capitalize())
        lines.append(f"### {label}")
        lines.append("")
        for c in groups[t]:
            summary = c.get("summary", c.get("message", ""))
            lines.append(f"- {summary}")
        lines.append("")
    if repo_url:
        lines.append(f"[{version}]: {repo_url}/releases/tag/{version}")
        lines.append("")
    return "\n".join(lines).strip()


def format_conventional_commits(
    version: str,
    groups: dict[str, list[dict[str, Any]]],
    repo_url: str = "",
    date_str: str | None = None,
) -> str:
    if date_str is None:
        date_str = date.today().isoformat()
    lines: list[str] = [
        f"## {version} ({date_str})",
        "",
    ]
    for t in TYPE_ORDER:
        if t not in groups:
            continue
        emoji = CONVENTIONAL_EMOJIS.get(t, "")
        for c in groups[t]:
            summary = c.get("summary", c.get("message", ""))
            prefix = f"{emoji} " if emoji else ""
            lines.append(f"{prefix}{summary}")
        lines.append("")
    return "\n".join(lines).strip()


def format_changelog(
    version: str,
    classifications: list[dict[str, Any]],
    fmt: str = "keep_a_changelog",
    repo_url: str = "",
) -> str:
    groups = group_by_type(classifications)
    if fmt == "conventional_commits":
        return format_conventional_commits(version, groups, repo_url)
    return format_keep_a_changelog(version, groups, repo_url)
