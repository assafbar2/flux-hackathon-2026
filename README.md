# Flux

The org as it runs, not as it is drawn.

Flux is a Google Cloud Rapid Agent Hackathon project for onboarding engineers into GitLab-based teams. It reads GitLab activity and an HR-maintained Notion guide, generates a day-one brief, answers grounded onboarding questions, and can assign a first GitLab issue after explicit confirmation.

## Why The Name

The org is always in flux. The org chart is a snapshot that is already stale the moment it is printed. Flux reads what is actually moving: commits, reviews, PRs, who is on leave, and what is on fire, then surfaces the living state of the team instead of the frozen official version.

It works on a second level too: a new hire is in flux. Week one is disorienting, and Flux meets them there with real intelligence instead of another static PDF.

## For Judges

Start here:

- Live app: https://flux-153593352872.us-central1.run.app
- Demo video: https://youtu.be/oIAdQKI1Kek
- Health check: https://flux-153593352872.us-central1.run.app/api/health
- Demo script: `docs/DEMO_SCRIPT.md`
- Agent Builder / Agent Platform proof: `docs/AGENT_BUILDER_PROOF.md`
- Submission checklist: `docs/submission-checklist.md`

The core evidence to verify:

1. Flux runs publicly on Cloud Run.
2. `/api/health` returns `mode: "live"`.
3. The backend uses Google ADK `LlmAgent` + `Runner`.
4. GitLab MCP is registered through `McpToolset` and `glab mcp serve`.
5. The confirmed assignment flow calls GitLab MCP `glab_issue_update`.

## Why Flux Exists

Onboarding today is mostly a static promise: a PDF, a wiki page, a few links, and a manager saying "just ask around." That material is usually stale before the new hire reads it. It describes the official org chart, but not the real operating system of the company: who actually reviews auth, which migration is politically sensitive, who is on leave, which Slack channels are performative, and which first task is safe.

The missing layer is **ground truth**. Companies already have it, but it is scattered across the work systems people use every day:

- GitLab knows what is actually changing, who reviews it, which issues are open, and where the safe first contribution lives.
- Notion knows the human context: team norms, availability, unwritten rules, meeting culture, and current priorities.
- Cloud Run and Google Cloud Agent Builder make that context available as a live, grounded agent instead of another stale document.

The beachhead is engineering onboarding for GitLab-based teams, but the broader TAM is workforce onboarding for every company whose work truth is split across collaboration tools. Every new engineer, support rep, operator, analyst, and manager needs the same thing on day one: not an org chart, but the living map of how the team works.

## Workforce Components

Flux is built for a modern company where HR and team leads maintain Notion, engineers work in GitLab, and new hires need a usable first-day experience without getting access to every internal system immediately.

```mermaid
flowchart LR
  NH["New hire"]
  Link["Flux hire link"]
  Brief["Flux Brief\nRight Now, People Map,\nWeek 1 Moves, Landmines"]
  Chat["Grounded chat\nwith sources"]
  Action["Confirmed action\nAssign first GitLab issue"]
  Notion["Notion team guide\nroles, norms, availability,\nunwritten rules"]
  GitLab["GitLab MCP server\nissues, owners, reviews,\nfirst tasks"]
  Agent["Google Cloud Agent Builder / ADK\nGemini reasoning + tool routing"]
  Run["Cloud Run\npublic demo app"]

  NH --> Link --> Run --> Agent
  Agent --> Notion
  Agent --> GitLab
  Agent --> Brief --> NH
  NH --> Chat --> Agent
  NH --> Action --> Agent --> GitLab
```

From the new hire's point of view, Flux is a single link. Behind the scenes, it grounds every answer in the systems the company already trusts.

## Screenshots

### Setup With Demo Data

Provision a new hire in one click and reveal a dynamic onboarding journey that changes as the team, work, and risks change.

![Flux setup page provisioning a new-hire journey](docs/screenshots/setup-demo-data.png)

### New-Hire Brief

The generated brief turns live engineering activity and team context into a grounded first-day map: what is active, who owns what, where to start, and what to avoid.

![Flux new-hire brief with right-now, people map, week-one moves, and landmines](docs/screenshots/new-hire-brief.png)

### Move Beyond Chat

Flux proposes a first real task and only writes to GitLab after confirmation.

![Flux chat showing issue assignment confirmed](docs/screenshots/assignment-confirmed.png)

## Live Demo

- App: https://flux-153593352872.us-central1.run.app
- Health check: https://flux-153593352872.us-central1.run.app/api/health
- Cloud Run service: `flux`
- Region: `us-central1`
- Current revision verified: `flux-00012-n47`

The setup page can be used with blank fields for the hackathon demo. Blank values create a workspace that uses deployed server-side configuration for live Notion, GitLab MCP, and Gemini/ADK orchestration.

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
- GitLab issue ingestion through the official GitLab CLI MCP server (`glab mcp serve`).
- Confirmed GitLab issue assignment through the MCP `glab_issue_update` tool.
- Google Cloud Agent Builder orchestration via the ADK Python SDK (`google.adk.agents.LlmAgent` + `google.adk.runners.Runner`), with Gemini as the reasoning layer and GitLab MCP registered as a callable toolset.
- Source attribution in the brief and chat.
- Explicit action confirmation before any GitLab write.

Important honesty for judges and reviewers:

- `FLUX_AGENT_MODE=live` is the current deployed mode.
- `GEMINI_MODEL=gemini-2.0-flash` is configured as the primary model, with `GEMINI_FALLBACK_MODEL=gemini-2.5-flash` because this Google Cloud project currently returns Vertex 404s for the Gemini 2.0 Flash model in the tested locations.
- Agent orchestration uses the code-first Google Agent Builder / Agent Platform path via the ADK Python SDK (`LlmAgent` + `Runner`) with the GitLab MCP server registered as a toolset. The production product is deployed on Cloud Run so judges can use the full React onboarding flow.
- Confirmed write actions are executed only after explicit user confirmation.

## Judging Fit

Contest judges score equally on technological implementation, design, potential impact, and quality of idea.

- **Technological implementation:** Cloud Run app, Gemini-powered ADK agent, GitLab MCP read/write tools, Notion ingestion, Secret Manager, fallback reliability, and backend tests.
- **Design:** one-link new-hire flow, visible demo mode, source attribution, four-section brief, and explicit confirmation before write actions.
- **Potential impact:** onboarding ramp is expensive and repeated across every growing team; Flux turns scattered work truth into useful day-one guidance.
- **Quality of idea:** Flux maps the living organization from actual work signals instead of repeating a stale org chart.

Agent Builder proof notes live in `docs/AGENT_BUILDER_PROOF.md`. Submission copy lives in `docs/DEVPOST_SUBMISSION.md`.

## Architecture

```text
React setup page
  -> POST /api/setup
  -> returns /onboard/{workspace_id}

React onboarding page
  -> GET /api/brief/{workspace_id}
  -> Notion API or fixture guide
  -> GitLab MCP issue reads via glab mcp serve
  -> Google ADK + Gemini synthesis
  -> Flux Brief

Chat
  -> POST /api/chat
  -> Google ADK + Gemini grounded answer with sources
  -> optional action proposal

Confirmed action
  -> POST /api/action/confirm
  -> GitLab MCP glab_issue_update assignment if live GitLab env vars are present
```

## Repository Layout

```text
backend/
  main.py                  FastAPI app and static frontend serving
  routes/                  setup, brief, chat, action confirmation
  services/                ADK agent, Notion, GitLab MCP, influence graph, fallback intelligence
  demo_data/               deterministic fallback data
  tests/                   backend test suite

frontend/
  src/pages/               setup and onboarding pages
  src/components/          brief, chat, source chips

docs/
  DEMO_SCRIPT.md           final hosted video script
  DEVPOST_SUBMISSION.md    submission form draft
  ROADMAP.md               next-step roadmap
  AGENT_BUILDER_PROOF.md   ADK / Agent Builder evidence
```

## Local Development

Create `.env` from `.env.example` and fill values as needed. Tokens must stay in `.env` or Secret Manager, never in git.

Install GitLab CLI locally before running live MCP mode:

```bash
brew install glab
```

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

This shell currently does not have Docker installed, so local container build verification may need to happen in Cloud Build.

## Cloud Run Deployment

The deployed service uses Cloud Run source deployment and Secret Manager. Example command shape:

```bash
gcloud run deploy flux \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_LOCATION=us-east4,GEMINI_MODEL=gemini-2.0-flash,GEMINI_FALLBACK_MODEL=gemini-2.5-flash,GITLAB_USERNAME=$GITLAB_USERNAME,GITLAB_PROJECT_URL=$GITLAB_PROJECT_URL,NOTION_PAGE_URL=$NOTION_PAGE_URL,FLUX_AGENT_MODE=live,FLUX_BASE_URL=$FLUX_BASE_URL,GLAB_COMMAND=glab" \
  --set-secrets "GITLAB_TOKEN=flux-gitlab-token:latest,NOTION_TOKEN=flux-notion-token:latest"
```

Required public access for judging:

```text
allUsers -> Cloud Run Invoker -> service flux
```

## Demo Resources

- Demo video: https://youtu.be/oIAdQKI1Kek
- Demo script: `docs/DEMO_SCRIPT.md`
- Roadmap: `docs/ROADMAP.md`
- Agent Builder proof notes: `docs/AGENT_BUILDER_PROOF.md`
- Submission form draft: `docs/DEVPOST_SUBMISSION.md`
- Submission checklist: `docs/submission-checklist.md`
- Notion guide shape: see `backend/demo_data/notion_page.md`
- GitLab demo issue flow: ask `Assign issue #412 to me`, then click `Confirm assignment`

## Submission Checklist

- Cloud Run URL is public and healthy.
- GitHub repo is public.
- MIT license remains present.
- Demo video is under 3 minutes.
- GitLab partner track is selected.
- README explains the live ADK, Gemini, GitLab MCP, Notion, and Cloud Run architecture.
