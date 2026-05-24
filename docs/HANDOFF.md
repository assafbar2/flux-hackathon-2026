# Flux Handoff

Last updated: May 24, 2026.

This file is for moving the project to Claude Code or another coding agent without losing state.

## Source

- Local path: `/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026`
- GitHub repo: `https://github.com/assafbar2/flux-hackathon-2026`
- Branch: `main`
- Current public app: https://flux-dpq2d26l7q-uc.a.run.app
- Cloud Run service: `flux`
- Region: `us-central1`
- Google Cloud project: `direct-subject-497307-p8`

## Current Deployment

- Latest verified revision: `flux-00004-dfs`
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
FLUX_AGENT_MODE=demo
```

This means:

- Notion is read live when `NOTION_TOKEN` and `NOTION_PAGE_URL` are available.
- GitLab issues and assignment are live when `GITLAB_TOKEN` and `GITLAB_PROJECT_URL` are available.
- Influence graph and chat synthesis are deterministic for demo reliability.
- Gemini 2.0 Flash and Agent Builder are planned but not yet the production orchestration path.
- `backend/services/gitlab_mcp.py` currently provides MCP-shaped operations over GitLab HTTP API calls.

## Verified Demo Flow

1. Open https://flux-dpq2d26l7q-uc.a.run.app
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
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GEMINI_MODEL=$GEMINI_MODEL,GITLAB_USERNAME=$GITLAB_USERNAME,GITLAB_PROJECT_URL=$GITLAB_PROJECT_URL,NOTION_PAGE_URL=$NOTION_PAGE_URL,FLUX_AGENT_MODE=demo,FLUX_BASE_URL=$URL" \
  --set-secrets "GITLAB_TOKEN=flux-gitlab-token:latest,NOTION_TOKEN=flux-notion-token:latest" \
  --quiet
```

## Important Files

- `README.md`: judge-facing setup and status.
- `docs/DEMO_SCRIPT.md`: recording and live-demo script.
- `backend/services/demo_intelligence.py`: deterministic brief and chat answers.
- `backend/services/gitlab_mcp.py`: GitLab issue read/write adapter.
- `backend/services/notion.py`: Notion page reader.
- `frontend/src/pages/Setup.tsx`: HR setup flow.
- `frontend/src/pages/Onboard.tsx`: new-hire brief and chat page.

## Known Gaps

- Official GitLab MCP server is not yet wired through Agent Builder.
- Gemini 2.0 Flash dependency exists, but current deployed synthesis is deterministic.
- Workspaces are stored in memory, so a Cloud Run cold restart loses generated links.
- The GitHub repo is currently private and must be made public before final hackathon submission.
- The GitLab token used during development should be rotated before any public demo or repo publication.

## Best Next Steps

1. Keep the current deployment stable for recording.
2. Record the 3-minute video using `docs/DEMO_SCRIPT.md`.
3. Make the GitHub repo public only after checking for secrets.
4. If time remains, wire Agent Builder + official GitLab MCP and keep deterministic mode as fallback.
