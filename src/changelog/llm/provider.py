from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def classify_commit(self, message: str) -> dict[str, Any]:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model

    async def classify_commit(self, message: str) -> dict[str, Any]:
        raise NotImplementedError("OpenAI classification not yet implemented")


class LocalLLMProvider(LLMProvider):
    def __init__(self, model_path: str = "") -> None:
        self.model_path = model_path

    async def classify_commit(self, message: str) -> dict[str, Any]:
        raise NotImplementedError("Local LLM classification not yet implemented")


def get_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    providers: dict[str, type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "local": LocalLLMProvider,
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return providers[provider_name](**kwargs)
