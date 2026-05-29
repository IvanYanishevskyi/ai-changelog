# GitLog — GitHub App Credential Deployment Guide
**Generated:** Day 14 | **Owner:** CTO | **Status:** Ready for deployment

---

## 🔐 Render Environment Variables

The Board has delivered GitHub App credentials. Set these on Render **immediately**.

### Step 1: Set environment variables on Render

Option A — Render Dashboard (recommended for secrets):
1. Go to https://dashboard.render.com/web/services/ai-changelog
2. Navigate to **Environment** tab
3. Add or update the following variables:

| Key | Value | Notes |
|-----|-------|-------|
| `GITHUB_APP_ID` | `3905523` | From Board delivery |
| `GITHUB_APP_PRIVATE_KEY` | *(full PEM content)* | Copy from `gitlog-ai-ai-changelog-generator.2026-05-29.private-key.pem` |
| `GITHUB_WEBHOOK_SECRET` | `a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954` | From Board delivery |
| `GITHUB_CLIENT_ID` | `Iv23liDhRCwkn09QRlqW` | GitHub App OAuth client ID |
| `GITHUB_OAUTH_REDIRECT_URI` | `https://gitlog.space/auth/github/callback` | Updated to production domain |

**⚠️ IMPORTANT:** The private key is a multi-line PEM file. Paste the **entire contents** including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`.

Option B — Render CLI (if authenticated):
```bash
# From project root
cd ai-changelog

render env set GITHUB_APP_ID "3905523" --service ai-changelog
render env set GITHUB_WEBHOOK_SECRET "a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954" --service ai-changelog
render env set GITHUB_CLIENT_ID "Iv23liDhRCwkn09QRlqW" --service ai-changelog
render env set GITHUB_OAUTH_REDIRECT_URI "https://gitlog.space/auth/github/callback" --service ai-changelog

# For the private key, use file input:
render env set GITHUB_APP_PRIVATE_KEY --file gitlog-ai-ai-changelog-generator.2026-05-29.private-key.pem --service ai-changelog
```

### Step 2: Verify env vars are set

After deployment, check the health endpoint:
```
GET https://ai-changelog-sc7o.onrender.com/health
```

Expected: `{"status":"ok"}`

### Step 3: Redeploy

After setting env vars, trigger a manual deploy from the Render dashboard or push a new commit to trigger auto-deploy.

---

## 🔗 GitHub App Configuration Checklist

After deploying credentials, configure the GitHub App at https://github.com/settings/apps/gitlog-ai:

| Setting | Value |
|---------|-------|
| **Webhook URL** | `https://gitlog.space/webhooks/github` *(updated from old Render URL)* |
| **Webhook Secret** | `a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954` |
| **Callback URL** | `https://gitlog.space/auth/github/callback` |
| **Homepage URL** | `https://gitlog.space` |

**Permissions required:**
- Repository permissions:
  - **Contents:** Read-only
  - **Metadata:** Read-only
  - **Pull requests:** Read & Write
- Organization permissions: None
- Subscribe to events: `push`, `release`, `installation`, `installation_repositories`

---

## 🧪 End-to-End Test Protocol

### Test 1: Webhook Signature Verification

```bash
curl -X POST https://gitlog.space/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=INVALID" \
  -d '{"repository":{"full_name":"test/test"},"ref":"refs/heads/main","commits":[]}'
```

Expected: `403 Invalid signature`

### Test 2: Simulate a Push Event (without LLM)

Use the test script at `tests/test_webhook_push.py` (see below) or run locally:

```bash
cd ai-changelog
python -m pytest tests/ -v
```

### Test 3: Real GitHub Integration

1. Install the GitHub App on a test repository (e.g., `TechVenture-Inc/ai-changelog`)
2. Push a commit with a message like `feat: add webhook test`
3. Verify webhook delivery in GitHub App → Advanced → Recent Deliveries
4. Check Render logs for: `Push event for repo: ...`
5. Verify changelog appears in dashboard API: `GET /api/dashboard`

---

## 📝 Notes

- `GITHUB_OAUTH_CLIENT_SECRET` is still required for the OAuth login flow. If using the GitHub App's OAuth credentials, generate a client secret from the GitHub App settings and set it as `GITHUB_OAUTH_CLIENT_SECRET`.
- The old Render URL (`ai-changelog-sc7o.onrender.com`) has been replaced with `gitlog.space` in all redirect URIs.
- Repository records are now automatically created on `installation_repositories` and `push` events, fixing the empty dashboard issue.
