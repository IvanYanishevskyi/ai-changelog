from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Changelog Generator"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/changelog"

    github_app_id: str = ""
    github_app_private_key: str = ""
    github_webhook_secret: str = ""

    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    github_oauth_redirect_uri: str = "https://gitlog.space/auth/github/callback"

    # GitHub App also exposes an OAuth client_id (aliases github_oauth_client_id)
    github_client_id: str = ""

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_provider: str = "openrouter"
    llm_model: str = "openai/gpt-4o-mini"

    sentry_dsn: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
