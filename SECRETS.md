# Secrets Reference

| Secret | Source | Status |
|--------|--------|--------|
| `GITHUB_APP_ID` | Board delivered | **DEPLOYED** — `3905523` |
| `GITHUB_APP_PRIVATE_KEY` | Board delivered | **DEPLOYED** — from `.pem` file |
| `GITHUB_WEBHOOK_SECRET` | Board delivered | **DEPLOYED** — `a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954` |
| `GITHUB_CLIENT_ID` | Board delivered | **DEPLOYED** — `Iv23liDhRCwkn09QRlqW` |
| `GITHUB_OAUTH_CLIENT_SECRET` | Existing OAuth App | **Still required** — set as Render env var |
| `JWT_SECRET` | Generated locally | **Ready** — set as Render env var |
| `OPENROUTER_API_KEY` | Board provided | **Ready** — set as Render env var |
| `SENTRY_DSN` | Sentry project settings | Optional for MVP |
| `DATABASE_URL` | Neon PostgreSQL | **LIVE** — Render-managed |

## GitHub App Configuration (Post-Deploy)

App: **Gitlog AI** | ID: `3905523`

After deploying credentials, configure at https://github.com/settings/apps/gitlog-ai:

| Setting | Value |
|---------|-------|
| **Webhook URL** | `https://gitlog.space/webhooks/github` |
| **Webhook Secret** | `a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954` |
| **Callback URL** | `https://gitlog.space/auth/github/callback` |
| **Homepage URL** | `https://gitlog.space` |

**Permissions:**
- Repository permissions:
  - Contents: Read-only
  - Metadata: Read-only
  - Pull requests: Read & Write
- Organization permissions: None

**Subscribe to events:** `push`, `release`, `installation`, `installation_repositories`

**Note:** Private key file is `gitlog-ai-ai-changelog-generator.2026-05-29.private-key.pem` in project root.