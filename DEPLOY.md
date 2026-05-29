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
| `GITHUB_OAUTH_CLIENT_SECRET` | *(generate from GitHub App settings)* | Generate in GitHub App → OAuth → Generate a new client secret |
| `GITHUB_OAUTH_REDIRECT_URI` | `https://ai-changelog-sc7o.onrender.com/auth/github/callback` | **Must point to the BACKEND**, not the frontend |

**⚠️ IMPORTANT:** The OAuth redirect URI MUST point to the backend Render URL, NOT the frontend (gitlog.space). GitHub redirects to this URL with the OAuth `code`, and the backend handles the token exchange. After successful auth, the backend redirects the user back to the frontend dashboard.

**⚠️ IMPORTANT:** The private key is a multi-line PEM file. Paste the **entire contents** including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`.

Option B — Render CLI (if authenticated):
```bash
# From project root
cd ai-changelog

render env set GITHUB_APP_ID "3905523" --service ai-changelog
render env set GITHUB_WEBHOOK_SECRET "a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954" --service ai-changelog
render env set GITHUB_CLIENT_ID "Iv23liDhRCwkn09QRlqW" --service ai-changelog
render env set GITHUB_OAUTH_REDIRECT_URI "https://ai-changelog-sc7o.onrender.com/auth/github/callback" --service ai-changelog

# For the private key, use file input:
render env set GITHUB_APP_PRIVATE_KEY --file gitlog-ai-ai-changelog-generator.2026-05-29.private-key.pem --service ai-changelog
```

### Step 2: Verify env vars are set

After deployment, check the login endpoint:
```bash
curl -si https://ai-changelog-sc7o.onrender.com/auth/login | grep location
```

Expected: `redirect_uri=https://ai-changelog-sc7o.onrender.com/auth/github/callback`

### Step 3: Redeploy

After setting env vars, trigger a manual deploy from the Render dashboard or push a new commit to trigger auto-deploy.

---

## 🔗 GitHub App Configuration Checklist

After deploying credentials, configure the GitHub App at https://github.com/settings/apps/gitlog-ai:

| Setting | Value |
|---------|-------|
| **Webhook URL** | `https://gitlog.space/webhooks/github` *(updated from old Render URL)* |
| **Webhook Secret** | `a8be30985431b93619f2bb489011d9c808e03c4d91ca114ee48ab8f33559b954` |
| **Callback URL** | `https://ai-changelog-sc7o.onrender.com/auth/github/callback` **← BACKEND URL** |
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

### Test 2: OAuth Login Flow

1. Go to `https://gitlog.space/dashboard`
2. Click "Login with GitHub"
3. You should be redirected to GitHub OAuth consent screen
4. After authorizing, you should be redirected back to `https://gitlog.space/dashboard/#access_token=...`
5. Dashboard loads with your GitHub profile

### Test 3: Real GitHub Integration

1. Install the GitHub App on a test repository (e.g., `TechVenture-Inc/ai-changelog`)
2. Push a commit with a message like `feat: add webhook test`
3. Verify webhook delivery in GitHub App → Advanced → Recent Deliveries
4. Check Render logs for: `Push event for repo: ...`
5. Verify changelog appears in dashboard API: `GET /api/dashboard`

---

## 📝 Notes

- `GITHUB_OAUTH_CLIENT_SECRET` is required for the OAuth login flow. Generate it from the GitHub App settings page under "OAuth" → "Generate a new client secret".
- The old Render URL (`ai-changelog-sc7o.onrender.com`) has been replaced with `gitlog.space` in all redirect URIs.
- Repository records are now automatically created on `installation_repositories` and `push` events, fixing the empty dashboard issue.
- **OAuth callback URL must always point to the backend**, never the frontend. The backend handles the code exchange and then redirects to the frontend dashboard with the JWT token.
