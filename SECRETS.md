# Secrets Reference

| Secret | Source | Status |
|--------|--------|--------|
| `GITHUB_APP_ID` | GitHub App settings page | Pending — create App |
| `GITHUB_APP_PRIVATE_KEY` | Downloaded from GitHub App settings | Pending — create App |
| `GITHUB_WEBHOOK_SECRET` | Generated locally | **Ready**: `759d26118129ad892bb9af122223c58def1821cbb34bb1f340b53d7e56cc1775` |
| `FLY_API_TOKEN` | Fly.io dashboard → Access Tokens | Pending — create Fly.io account |
| `OPENAI_API_KEY` | Board to provide | Blocked |
| `SENTRY_DSN` | Sentry project settings | Optional for MVP |

## GitHub App Creation Checklist

1. Go to https://github.com/settings/apps
2. Name: `AI Changelog Generator`
3. Homepage URL: repo URL (set after creation)
4. Webhook URL: `https://ai-changelog-staging.fly.dev/webhooks/github`
5. Webhook Secret: `759d26118129ad892bb9af122223c58def1821cbb34bb1f340b53d7e56cc1775`
6. Permissions:
   - **Repository permissions:**
     - Contents: Read-only
     - Metadata: Read-only
     - Pull requests: Read & Write
   - **Organization permissions:** None
7. Events: `push`, `release`, `installation`
8. Generate private key → download `.pem` file
9. Note the **App ID** from the settings page
