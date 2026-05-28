from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CLASSIFY_SYSTEM_PROMPT = """\
You are a commit message classifier. Given a git commit message, return JSON:
{
  "type": "feat" | "fix" | "chore" | "docs" | "perf" | "refactor" | "test" | "style" | "breaking",
  "summary": "human-readable one-liner describing what changed",
  "is_breaking_change": false
}

Rules:
- feat: a new feature
- fix: a bug fix
- chore: maintenance, tooling, dependencies
- docs: documentation only
- perf: performance improvement
- refactor: code restructuring without feature/bug change
- test: adding or modifying tests
- style: formatting, whitespace
- breaking: breaking API change (overrides any other type)
- is_breaking_change: true if commit contains BREAKING CHANGE, ! prefix, or breaking change
- summary: max 80 chars, present tense, no leading capital
"""


class LLMProvider(ABC):
    @abstractmethod
    async def classify_commit(self, message: str) -> dict[str, Any]:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(
        self, api_key: str, model: str = "openai/gpt-4o-mini", base_url: str = "https://api.openai.com/v1"
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    async def classify_commit(self, message: str) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("API key not configured")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Classify this commit message:\n\n{message}"},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 150,
                },
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            content = data["choices"][0]["message"]["content"]
            cleaned = content.strip()
            for p in ("```json", "```"):
                cleaned = cleaned.removeprefix(p).removesuffix(p)
            cleaned = cleaned.strip()
            result: dict[str, Any] = json.loads(cleaned)
            return result


class OpenRouterProvider(OpenAIProvider):
    def __init__(
        self, api_key: str, model: str = "openai/gpt-4o-mini", base_url: str = "https://openrouter.ai/api/v1"
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url)


class LocalLLMProvider(LLMProvider):
    def __init__(self, model_path: str = "") -> None:
        self.model_path = model_path

    async def classify_commit(self, message: str) -> dict[str, Any]:
        raise NotImplementedError("Local LLM classification not yet implemented")


def get_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    providers: dict[str, type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "openrouter": OpenRouterProvider,
        "local": LocalLLMProvider,
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return providers[provider_name](**kwargs)
