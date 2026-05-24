# Flux

The org as it runs, not as it is drawn.

Flux is a Google Cloud Rapid Agent Hackathon project for onboarding engineers into GitLab-based teams. It reads GitLab activity and an HR-maintained Notion guide, generates a day-one brief, answers grounded onboarding questions, and can assign a first GitLab issue after explicit confirmation.

## Live Demo

- App: https://flux-dpq2d26l7q-uc.a.run.app
- Health check: https://flux-dpq2d26l7q-uc.a.run.app/api/health
- Cloud Run service: `flux`
- Region: `us-central1`
- Current revision verified: `flux-00004-dfs`

The setup page can be used with blank fields for the hackathon demo. Blank values create a demo workspace using the deployed server-side configuration and deterministic fallback data where needed.

## What It Does

1. HR opens Flux and generates a unique new-hire link.
2. The new hire opens `/onboard/{workspace_id}`.
3. Flux shows a four-part brief:
   - `Right Now`: live blockers and what to avoid this week.
   - `Your People Map`: who actually owns which systems.
   - `Week 1 Moves`: safe first tasks.
   - `Landmines`: unwritten rules from the team guide.
4. The new hire asks follow-up questions with source attribution.
5. When the new hire asks to take issue `#412`, Flux proposes a GitLab assignment and waits for confirmation before writing.

## Current Build Status

Implemented and verified:

- React + TypeScript + Vite frontend.
- FastAPI backend served from one Cloud Run service.
- Public Cloud Run deployment.
- Secret Manager wiring for GitLab and Notion tokens.
- Notion page ingestion with fixture fallback.
- GitLab issue ingestion and confirmed assignment against a live GitLab project.
- Deterministic influence graph and chat answers for a reliable demo.
- Source attribution in the brief and chat.
- Explicit action confirmation before any GitLab write.

Important honesty for judges and reviewers:

- `FLUX_AGENT_MODE=demo` is the current deployed mode.
- Gemini 2.0 Flash and Agent Builder are the intended orchestration path, but the current judged demo uses deterministic synthesis for reliability.
- `backend/services/gitlab_mcp.py` exposes MCP-shaped operations, but currently calls GitLab's HTTP API directly until the official GitLab MCP runtime is wired through Agent Builder.

## Architecture

```text
React setup page
  -> POST /api/setup
  -> returns /onboard/{workspace_id}

React onboarding page
  -> GET /api/brief/{workspace_id}
  -> Notion API or fixture guide
  -> GitLab activity or fixture review graph
  -> deterministic Flux Brief

Chat
  -> POST /api/chat
  -> grounded answer with sources
  -> optional action proposal

Confirmed action
  -> POST /api/action/confirm
  -> GitLab assignment if live GitLab env vars are present
```

## Repository Layout

```text
backend/
  main.py                  FastAPI app and static frontend serving
  routes/                  setup, brief, chat, action confirmation
  services/                Notion, GitLab, influence graph, demo intelligence
  demo_data/               deterministic fallback data
  tests/                   backend test suite

frontend/
  src/pages/               setup and onboarding pages
  src/components/          brief, chat, source chips

docs/
  DEMO_SCRIPT.md           3-minute video and live demo script
  HANDOFF.md               current state for another coding agent
```

## Local Development

Create `.env` from `.env.example` and fill values as needed. Tokens must stay in `.env` or Secret Manager, never in git.

Start the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Test And Build

Backend:

```bash
backend/.venv/bin/pytest backend/tests -v
```

Frontend:

```bash
cd frontend
npm run build
```

Container build path:

```bash
docker build -t flux .
```

## Cloud Run Deployment

The deployed service uses Cloud Run source deployment and Secret Manager. Example command shape:

```bash
gcloud run deploy flux \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GEMINI_MODEL=$GEMINI_MODEL,GITLAB_USERNAME=$GITLAB_USERNAME,GITLAB_PROJECT_URL=$GITLAB_PROJECT_URL,NOTION_PAGE_URL=$NOTION_PAGE_URL,FLUX_AGENT_MODE=demo,FLUX_BASE_URL=$FLUX_BASE_URL" \
  --set-secrets "GITLAB_TOKEN=flux-gitlab-token:latest,NOTION_TOKEN=flux-notion-token:latest"
```

Required public access for judging:

```text
allUsers -> Cloud Run Invoker -> service flux
```

## Demo Resources

- Demo script: `docs/DEMO_SCRIPT.md`
- Handoff notes: `docs/HANDOFF.md`
- Notion guide shape: see `backend/demo_data/notion_page.md`
- GitLab demo issue flow: ask `Assign issue #412 to me`, then click `Confirm assignment`

## Submission Checklist

- Cloud Run URL is public and healthy.
- GitHub repo is switched from private to public before final submission.
- MIT license remains present.
- Demo video is under 3 minutes.
- GitLab partner track is selected.
- README explains what is live now and what remains planned.
