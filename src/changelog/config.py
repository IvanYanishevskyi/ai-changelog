from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Changelog Generator"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/changelog"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    github_app_id: str = ""
    github_app_private_key: str = ""
    github_webhook_secret: str = ""

    openai_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"

    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
