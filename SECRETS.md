# Secrets Reference

| Secret | Source | Status |
|--------|--------|--------|
| `GITHUB_APP_ID` | GitHub App settings page | Pending — create App |
| `GITHUB_APP_PRIVATE_KEY` | Downloaded from GitHub App settings | Pending — create App |
| `GITHUB_WEBHOOK_SECRET` | Generated locally | **Ready** — set as Render env var |
| `OPENROUTER_API_KEY` | Board provided | **Ready** — set as Render env var |
| `SENTRY_DSN` | Sentry project settings | Optional for MVP |
| `DATABASE_URL` | Neon PostgreSQL dashboard | Pending — create Neon project |

## GitHub App Creation Checklist

1. Go to https://github.com/settings/apps
2. Name: `AI Changelog Generator`
3. Homepage URL: `https://github.com/TechVenture-Inc/ai-changelog`
4. Webhook URL: `https://<BACKEND-URL>/webhooks/github` (set after backend hosting is decided)
5. Webhook Secret: `0b38e7ae7f864a1ab3ade63e9fdaada7803c0ee62c823f4cfa4b30868c6d16c9` (set as Render env var `GITHUB_WEBHOOK_SECRET`)
6. Permissions:
   - **Repository permissions:**
     - Contents: Read-only
     - Metadata: Read-only
     - Pull requests: Read & Write
   - **Organization permissions:** None
7. Events: `push`, `release`, `installation`
8. Generate private key → download `.pem` file
9. Note the **App ID** from the settings page