from __future__ import annotations

import pytest
import pytest_httpx

from changelog.llm.formatter import format_changelog, group_by_type
from changelog.llm.provider import OpenRouterProvider

FEAT_CONTENT = '{"type":"feat","summary":"add user login endpoint","is_breaking_change":false}'
FIX_CONTENT = (
    '{"type":"fix","summary":"fix null pointer in parser","is_breaking_change":false}'
)
BREAKING_CONTENT = (
    '{"type":"breaking","summary":"remove deprecated v1 API","is_breaking_change":true}'
)


@pytest.mark.asyncio
async def test_classify_commit_calls_api(httpx_mock: pytest_httpx.HTXTMock) -> None:
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-4o-mini")
    httpx_mock.add_response(json={"choices": [{"message": {"content": FEAT_CONTENT}}]})
    result = await provider.classify_commit("feat: add user login endpoint")
    assert result["type"] == "feat"
    assert result["summary"] == "add user login endpoint"
    assert result["is_breaking_change"] is False


@pytest.mark.asyncio
async def test_classify_commit_strips_json_fence(
    httpx_mock: pytest_httpx.HTXTMock,
) -> None:
    provider = OpenRouterProvider(api_key="test-key", model="openai/gpt-4o-mini")
    httpx_mock.add_response(
        json={
            "choices": [{
                "message": {
                    "content": f"```json\n{FIX_CONTENT}\n```"
                }
            }]
        }
    )
    result = await provider.classify_commit("fix: null pointer in parser")
    assert result["type"] == "fix"
    assert result["summary"] == "fix null pointer in parser"


@pytest.mark.asyncio
async def test_classify_commit_breaking(httpx_mock: pytest_httpx.HTXTMock) -> None:
    provider = OpenRouterProvider(api_key="test-key")
    httpx_mock.add_response(
        json={"choices": [{"message": {"content": BREAKING_CONTENT}}]}
    )
    result = await provider.classify_commit("feat!: remove deprecated v1 API")
    assert result["type"] == "breaking"
    assert result["is_breaking_change"] is True


def test_group_by_type() -> None:
    classifications = [
        {"type": "feat", "summary": "add login"},
        {"type": "fix", "summary": "fix crash"},
        {"type": "feat", "summary": "add logout"},
        {"type": "chore", "summary": "update deps"},
    ]
    groups = group_by_type(classifications)
    assert len(groups["feat"]) == 2
    assert len(groups["fix"]) == 1
    assert len(groups["chore"]) == 1


def test_format_keep_a_changelog() -> None:
    classifications = [
        {"type": "feat", "summary": "add user login"},
        {"type": "feat", "summary": "add export feature"},
        {"type": "fix", "summary": "fix null pointer"},
    ]
    result = format_changelog("v1.0.0", classifications, fmt="keep_a_changelog")
    assert "## [v1.0.0]" in result
    assert "### Added" in result
    assert "### Fixed" in result
    assert "- add user login" in result
    assert "- fix null pointer" in result


def test_format_conventional_commits() -> None:
    classifications = [
        {"type": "feat", "summary": "add user login"},
        {"type": "fix", "summary": "fix null pointer"},
    ]
    result = format_changelog("v1.0.0", classifications, fmt="conventional_commits")
    assert "## v1.0.0" in result
    assert ":sparkles:" in result
    assert ":bug:" in result
    assert "add user login" in result
