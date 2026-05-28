from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Changelog Generator"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/changelog"

    github_app_id: str = ""
    github_app_private_key: str = ""
    github_webhook_secret: str = ""

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_provider: str = "openrouter"
    llm_model: str = "openai/gpt-4o-mini"

    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
