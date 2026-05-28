# AI Changelog Generator

AI-powered changelog generator: parses git commits, classifies via LLM, outputs semantic changelogs (Markdown, JSON, Slack).

## Architecture

- **API**: FastAPI + Uvicorn
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Task Queue**: Celery + Redis
- **LLM**: Dual provider (OpenAI / local)
- **Hosting**: Fly.io
- **CI/CD**: GitHub Actions

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=changelog postgres:16

# Start Redis
docker run -d -p 6379:6379 redis:7

# Copy env and fill in secrets
cp .env.example .env

# Run database migrations
alembic upgrade head

# Run API
uvicorn changelog.main:app --reload

# Run Celery worker (separate terminal)
celery -A changelog.workers.celery_app worker --loglevel=info
```

## Project Structure

```
src/changelog/
  main.py          - FastAPI application entry point
  config.py        - Pydantic settings (env-based)
  health.py        - Health/readiness endpoints
  db/
    __init__.py    - Database session management
    base.py        - SQLAlchemy declarative base
    models.py      - Database models (Installation, Repository, Changelog)
  webhooks/
    github.py      - GitHub App webhook receiver
  workers/
    celery_app.py  - Celery app + task definitions
  llm/
    provider.py    - LLM provider abstraction (OpenAI / local)
alembic/           - Database migrations
tests/             - pytest test suite
```

## Endpoints

| Method | Path              | Description                    |
|--------|-------------------|--------------------------------|
| GET    | `/health`         | Health check (Redis + Postgres)|
| GET    | `/ready`          | Readiness probe                |
| POST   | `/webhooks/github`| GitHub webhook receiver        |

## Deployment

Push to `main` triggers GitHub Actions: lint + typecheck + test, then auto-deploy to Fly.io staging.

```bash
flyctl deploy
```

## Secrets (Fly.io)

```bash
flyctl secrets set OPENAI_API_KEY=... GITHUB_WEBHOOK_SECRET=... SENTRY_DSN=...
```
