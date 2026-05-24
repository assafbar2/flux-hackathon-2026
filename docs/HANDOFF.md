# Flux Handoff

Last updated: May 24, 2026.

This file is for moving the project to Claude Code or another coding agent without losing state.

## Source

- Local path: `/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026`
- GitHub repo: `https://github.com/assafbar2/flux-hackathon-2026`
- Branch: `main`
- Current public app: https://flux-153593352872.us-central1.run.app
- Cloud Run service: `flux`
- Region: `us-central1`
- Google Cloud project: `direct-subject-497307-p8`

## Current Deployment

- Latest verified revision: `flux-00010-vr5`
- Public health check verified: `GET /api/health` returns `{"status":"ok"}`
- Required public IAM binding is in place:

```text
allUsers -> roles/run.invoker -> Cloud Run service flux
```

- Secret Manager secrets:

```text
flux-gitlab-token
flux-notion-token
```

Do not print or commit secret values. Local `.env` is chmod `600` and gitignored.

## Current Mode

The app is deployed with:

```text
FLUX_AGENT_MODE=live
```

This means:

- Notion is read live when `NOTION_TOKEN` and `NOTION_PAGE_URL` are available.
- GitLab issue reads use the official GitLab CLI MCP server via `glab mcp serve`.
- GitLab assignment uses the MCP `glab_issue_update` tool after explicit confirmation.
- Brief and chat synthesis route through Google ADK (`LlmAgent` + `Runner`) with Gemini.
- `GEMINI_MODEL=gemini-2.0-flash` is configured as primary; `GEMINI_FALLBACK_MODEL=gemini-2.5-flash` is configured because the project currently returns Vertex 404s for Gemini 2.0 Flash in tested locations.
- Deterministic responses remain as fallback if ADK/Gemini fails.

## Verified Demo Flow

1. Open https://flux-153593352872.us-central1.run.app
2. Leave setup fields blank.
3. Click `Generate link`.
4. Open generated `/onboard/{workspace_id}` link.
5. Confirm the brief renders:
   - `Right Now`
   - `Your People Map`
   - `Week 1 Moves`
   - `Landmines`
6. Ask:

```text
Assign issue #412 to me
```

7. Flux should return an action proposal.
8. Click `Confirm assignment` to write to GitLab.

## Local Commands

Backend:

```bash
cd "/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026"
backend/.venv/bin/pytest backend/tests -v
```

Frontend:

```bash
cd "/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026/frontend"
npm run build
```

Deploy update:

```bash
cd "/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026"
set -a; source .env; set +a
GCLOUD="/Users/assafbarnir/1Code/Google Cloud CLI/google-cloud-sdk/bin/gcloud"
URL=$("$GCLOUD" run services describe flux --region us-central1 --project "$GOOGLE_CLOUD_PROJECT" --format='value(status.url)')
"$GCLOUD" run deploy flux \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash,GEMINI_FALLBACK_MODEL=gemini-2.5-flash,GITLAB_USERNAME=$GITLAB_USERNAME,GITLAB_PROJECT_URL=$GITLAB_PROJECT_URL,NOTION_PAGE_URL=$NOTION_PAGE_URL,FLUX_AGENT_MODE=live,FLUX_BASE_URL=$URL,GLAB_COMMAND=glab" \
  --set-secrets "GITLAB_TOKEN=flux-gitlab-token:latest,NOTION_TOKEN=flux-notion-token:latest" \
  --quiet
```

## Important Files

- `README.md`: judge-facing setup and status.
- `docs/DEMO_SCRIPT.md`: recording and live-demo script.
- `backend/services/agent_builder.py`: Google ADK + Gemini orchestration and fallback routing.
- `backend/services/demo_intelligence.py`: deterministic fallback brief and chat answers.
- `backend/services/gitlab_mcp.py`: official GitLab CLI MCP read/write adapter.
- `backend/services/notion.py`: Notion page reader.
- `frontend/src/pages/Setup.tsx`: HR setup flow.
- `frontend/src/pages/Onboard.tsx`: new-hire brief and chat page.

## Known Gaps

- The app uses Google ADK on Cloud Run, not a separate Vertex AI Agent Engine deployment.
- Gemini 2.0 Flash is configured primary, but the live project currently falls back to Gemini 2.5 Flash because Vertex returns 404 for 2.0 Flash in tested locations.
- GitLab MCP currently reads issues and writes assignment. Merge request and commit/review graph coverage can be expanded next.
- Workspaces are stored in memory, so a Cloud Run cold restart loses generated links.
- The GitHub repo is currently private and must be made public before final hackathon submission.
- The GitLab token used during development should be rotated before any public demo or repo publication.

## Best Next Steps

1. Keep the current deployment stable for recording.
2. Record the 3-minute video using `docs/DEMO_SCRIPT.md`.
3. Make the GitHub repo public only after checking for secrets.
4. If time remains, expand GitLab MCP reads beyond issues into merge requests, commits, and review signals.
