from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def classify_commit(self, message: str) -> dict:
        ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def classify_commit(self, message: str) -> dict:
        raise NotImplementedError("OpenAI classification not yet implemented")


class LocalLLMProvider(LLMProvider):
    def __init__(self, model_path: str = ""):
        self.model_path = model_path

    async def classify_commit(self, message: str) -> dict:
        raise NotImplementedError("Local LLM classification not yet implemented")


def get_provider(provider_name: str, **kwargs) -> LLMProvider:
    providers = {
        "openai": OpenAIProvider,
        "local": LocalLLMProvider,
    }
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    return providers[provider_name](**kwargs)
