# Flux Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Flux, a Google Cloud hosted onboarding intelligence agent that reads GitLab activity and a Notion team guide, generates a grounded new-hire brief, answers follow-up questions, and assigns a first issue after explicit confirmation.

**Architecture:** Use a Vite React frontend and a thin FastAPI backend deployed to Cloud Run. The backend owns setup links, Notion ingestion, GitLab MCP access, influence graph normalization, Gemini/Agent Builder prompting, chat, and confirmed GitLab write actions.

**Tech Stack:** React, TypeScript, Vite, FastAPI, Python, Google Cloud Run, Google Cloud Agent Builder, Gemini 2.0 Flash, GitLab MCP, Notion public API, Secret Manager, Docker.

---

## Current Status Update (May 24, 2026)

This plan has been implemented into a live Cloud Run service:

- Live app: `https://flux-153593352872.us-central1.run.app`
- Current revision: `flux-00009-gtn`
- Runtime mode: `FLUX_AGENT_MODE=live`
- Agent orchestration: Google ADK `LlmAgent` + `Runner` on Cloud Run, with Gemini as the reasoning layer.
- Gemini config: `gemini-2.0-flash` primary, `gemini-2.5-flash` fallback because this project currently returns Vertex 404s for Gemini 2.0 Flash in tested locations.
- GitLab integration: official GitLab CLI MCP server via `glab mcp serve`, using `glab_issue_list` for reads and `glab_issue_update` for confirmed assignment.
- Notion integration: live Notion API reader with deterministic fallback.

The older checklist below remains useful as execution history, but current source of truth is `README.md`, `docs/HANDOFF.md`, and the code.

---

## Current Sources

- Local requirements: `Google Hackathon - June 2026/AGENTS.md`
- Local product spec: `Google Hackathon - June 2026/flux-design-spec.md`
- Working assumption: local files are the current source of truth for scope, because live Devpost verification was blocked or unresolved during planning.

## Required Hackathon Tools

- Google Cloud Agent Builder: required orchestration layer.
- Gemini 2.0 Flash: required model per local instructions.
- GitLab MCP official partner server: required GitLab partner integration, including read and write operations.
- Google Cloud Run: required hosted app target.
- GitLab write action: required demo moment for "move beyond chat"; use explicit human confirmation before assigning an issue.
- MIT license and public GitHub repo: required for submission.

## Build Strategy

Build the demo path first, then harden it. The winning path is not a generic onboarding platform; it is one crisp demo where the brief exposes the "real org" and then turns guidance into an assigned GitLab issue.

### Recommended Approach

Use FastAPI + React, with local JSON/in-memory storage for demo workspaces. This matches the existing spec, keeps Cloud Run deployment simple, and avoids losing time to auth, databases, and multi-tenant plumbing.

### Rejected Alternatives

- Full Next.js app: simpler deployment shape, but Python is better for rapid backend service composition around MCP and data normalization.
- Database-backed SaaS: more production-like, but explicitly out of scope and too slow for the hackathon.
- Raw GitLab REST only: faster initially, but misses the required GitLab MCP partner integration.

---

## Phase 0: Account, Credit, And Repo Setup

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 0.1: Redeem the Google Cloud credit**

Open `https://console.cloud.google.com/billing` in the browser, redeem the available $100 credit, and confirm the billing account is attached to the project that will host Flux. Do this before deploying anything. The local instructions say the credit expires June 4, 2026.

- [ ] **Step 0.2: Create or select a Google Cloud project**

Use one project for all Flux resources.

```bash
gcloud projects create flux-hackathon-2026 --name="Flux Hackathon"
gcloud config set project flux-hackathon-2026
```

If the project already exists, only run:

```bash
gcloud config set project flux-hackathon-2026
```

- [ ] **Step 0.3: Enable required Google Cloud APIs**

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

Expected: all commands complete without permission errors.

- [ ] **Step 0.4: Initialize a public-ready repo**

If this folder is not already a git repo:

```bash
cd "/Users/assafbarnir/1Code/Codex Folder/Google Hackathon - June 2026"
git init
```

Do not commit secrets. The repo must be public for submission, with MIT license visible.

- [ ] **Step 0.5: Create base project metadata**

`LICENSE` should use the standard MIT text.

`.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
node_modules/
dist/
.DS_Store
*.log
```

`.env.example`:

```dotenv
GOOGLE_CLOUD_PROJECT=flux-hackathon-2026
GEMINI_MODEL=gemini-2.0-flash
GITLAB_TOKEN=
GITLAB_USERNAME=
NOTION_TOKEN=
FLUX_BASE_URL=http://localhost:5173
```

`README.md` must include:

```markdown
# Flux

The org as it runs, not as it's drawn.

Flux is a Google Cloud Rapid Agent Hackathon project for onboarding engineers into GitLab-based teams. It reads GitLab activity and a Notion team guide, generates a Flux Brief, answers grounded onboarding questions, and can assign a first GitLab issue after confirmation.

## Required Integrations

- Google Cloud Agent Builder
- Gemini 2.0 Flash
- GitLab MCP
- Notion API
- Google Cloud Run

## Local Development

1. Copy `.env.example` to `.env`.
2. Fill in Google Cloud, GitLab, and Notion values.
3. Start the backend.
4. Start the frontend.
5. Open `/setup`.
```

- [ ] **Step 0.6: Commit Phase 0**

```bash
git add README.md LICENSE .env.example .gitignore
git commit -m "chore: initialize flux hackathon repo"
```

---

## Phase 1: Running Skeleton

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/pages/Setup.tsx`
- Create: `frontend/src/pages/Onboard.tsx`
- Create: `frontend/src/components/FluxBrief.tsx`
- Create: `frontend/src/components/Chat.tsx`
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/routes/setup.py`
- Create: `backend/routes/brief.py`
- Create: `backend/routes/chat.py`
- Create: `backend/services/store.py`

- [ ] **Step 1.1: Scaffold the frontend**

Create a Vite React TypeScript app in `frontend/`. Keep it minimal: two routes, setup and onboard.

Run:

```bash
cd frontend
npm install
npm run dev
```

Expected: Vite starts locally and renders the setup page.

- [ ] **Step 1.2: Scaffold the backend**

`backend/requirements.txt`:

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
pydantic==2.11.5
python-dotenv==1.1.0
httpx==0.28.1
google-cloud-aiplatform==1.94.0
```

`backend/main.py` should create the app, enable CORS for local Vite, and include setup, brief, and chat routers under `/api`.

Run:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Expected: `GET http://localhost:8000/docs` opens FastAPI docs.

- [ ] **Step 1.3: Implement stub routes**

`POST /api/setup` accepts `gitlab_token`, `notion_url`, and optional `gitlab_username`; returns `{ "workspace_id": "...", "hire_link": "..." }`.

`GET /api/brief/{workspace_id}` returns a stub Flux Brief with the four required sections.

`POST /api/chat` returns a stub grounded answer and a stub source list.

- [ ] **Step 1.4: Connect frontend to stubs**

Setup page submits to `/api/setup` and displays the generated link.

Onboard page loads `/api/brief/{workspace_id}` and renders:

- Right Now
- Your People Map
- Week 1 Moves
- Landmines
- Chat input and answer history

- [ ] **Step 1.5: Verify full skeleton flow**

Run backend and frontend. In the browser:

1. Open `/setup`.
2. Submit fake values.
3. Click or paste generated `/onboard/{workspace_id}` link.
4. Confirm stub brief renders.
5. Ask a chat question and confirm a stub answer appears.

- [ ] **Step 1.6: Commit Phase 1**

```bash
git add frontend backend
git commit -m "feat: add flux skeleton app"
```

---

## Phase 2: Demo Data And Deterministic Intelligence

**Files:**
- Create: `backend/demo_data/notion_page.md`
- Create: `backend/demo_data/gitlab_activity.json`
- Create: `backend/services/notion_parser.py`
- Create: `backend/services/influence_graph.py`
- Create: `backend/tests/test_notion_parser.py`
- Create: `backend/tests/test_influence_graph.py`
- Modify: `backend/routes/brief.py`
- Modify: `backend/routes/chat.py`

- [ ] **Step 2.1: Add demo Notion content**

Create `backend/demo_data/notion_page.md` using the local AGENTS demo page content. Include all four sections:

- The Team (Real Talk)
- Right Now
- Unwritten Rules
- How to Ship Here

- [ ] **Step 2.2: Add deterministic GitLab activity fixture**

Create `backend/demo_data/gitlab_activity.json` with enough data to support the demo claims:

- Marcus reviewed about 71% of auth PRs.
- Dev is strongest on infra.
- Billing issue `#412` is open, unassigned, and good-first.
- Notifications issue `#89` is open and well-scoped.
- Auth has active P1 risk.

- [ ] **Step 2.3: Write parser tests**

Test that `notion_parser.py` returns exactly four section keys and preserves the important bullets for Sarah leave, Friday deploys, GraphQL landmine, and issue `#412`.

Run:

```bash
cd backend
pytest tests/test_notion_parser.py -v
```

Expected first run before implementation: fails because parser does not exist.

- [ ] **Step 2.4: Implement Notion section parser**

Build a small parser that accepts markdown-like block text and returns:

```python
{
    "team": "...",
    "right_now": "...",
    "unwritten_rules": "...",
    "how_to_ship": "..."
}
```

Keep it deterministic and easy to replace with live Notion API data later.

- [ ] **Step 2.5: Write influence graph tests**

Test that `influence_graph.py` returns Marcus as auth owner, Dev as infra owner, fastest reviewer order, active fires, and good-first issue candidates.

Run:

```bash
cd backend
pytest tests/test_influence_graph.py -v
```

Expected first run before implementation: fails because graph builder does not exist.

- [ ] **Step 2.6: Implement influence graph**

Compute:

- reviewer percentage by area
- owner by area
- average review turnaround by person
- open P1/P0 issues
- unassigned good-first issues
- high-churn files or modules

Return a normalized object the prompts can consume.

- [ ] **Step 2.7: Replace stub brief with deterministic brief**

Use parsed Notion content plus influence graph output to generate a deterministic brief before Gemini is wired in. This gives the demo a reliable fallback if live Agent Builder setup slips.

- [ ] **Step 2.8: Replace stub chat with deterministic answers for the demo questions**

Support at least these exact questions:

- Who actually owns the auth system?
- Who should I avoid pinging right now?
- What should I work on to make an impact in week 1?
- Is there anything I shouldn't say in standup?
- How do I get a PR merged fast?
- Which meetings actually matter?
- What's the fastest way to understand this codebase?
- Can you assign issue #412 to me?

Every answer must include source labels: GitLab activity, team guide, or both.

- [ ] **Step 2.9: Commit Phase 2**

```bash
git add backend
git commit -m "feat: add deterministic flux intelligence"
```

---

## Phase 3: Live Notion Ingestion

**Files:**
- Create: `backend/services/notion.py`
- Create: `backend/tests/test_notion.py`
- Modify: `backend/routes/brief.py`
- Modify: `.env.example`

- [ ] **Step 3.1: Implement Notion page ID extraction**

Accept full Notion URLs and extract the page ID. Test common Notion URL shapes.

- [ ] **Step 3.2: Implement recursive Notion block fetch**

Use `GET /v1/blocks/{block_id}/children` recursively. Convert blocks to markdown-like text before passing to the parser from Phase 2.

- [ ] **Step 3.3: Add fallback behavior**

If `NOTION_TOKEN` or a valid Notion page is missing, load `backend/demo_data/notion_page.md` and mark the source as demo data. This keeps judge demos from dying during setup.

- [ ] **Step 3.4: Verify with the demo Notion page**

Run:

```bash
cd backend
pytest tests/test_notion.py tests/test_notion_parser.py -v
```

Expected: all pass.

- [ ] **Step 3.5: Commit Phase 3**

```bash
git add backend .env.example
git commit -m "feat: add notion ingestion"
```

---

## Phase 4: GitLab MCP Integration

**Files:**
- Create: `backend/services/gitlab_mcp.py`
- Create: `backend/tests/test_gitlab_mcp_normalize.py`
- Modify: `backend/services/influence_graph.py`
- Modify: `.env.example`

- [ ] **Step 4.1: Install and document official GitLab MCP setup**

Find the official GitLab MCP server instructions and add exact local setup commands to `README.md`. The project must not silently use raw REST in place of MCP.

- [ ] **Step 4.2: Define normalized GitLab activity schema**

Normalize MCP outputs to the same shape used by `backend/demo_data/gitlab_activity.json`:

- projects
- commits
- merge requests
- reviews
- issues

- [ ] **Step 4.3: Implement read calls**

Implement wrapper methods for:

- `list_projects`
- `list_commits`
- `list_merge_requests`
- `list_issues`

Filter to last 90 days and repos with recent activity.

- [ ] **Step 4.4: Implement write calls behind a confirmation boundary**

Implement wrapper methods for:

- `assign_issue`
- `create_issue_comment`

Do not call these directly from normal chat. The route must first return an `action` object, then execute only after `/api/action/confirm`.

- [ ] **Step 4.5: Add fallback behavior**

If GitLab MCP is unavailable locally, load `backend/demo_data/gitlab_activity.json` and mark the source as demo data. The UI should still demo the product.

- [ ] **Step 4.6: Verify normalization tests**

Run:

```bash
cd backend
pytest tests/test_gitlab_mcp_normalize.py tests/test_influence_graph.py -v
```

Expected: all pass.

- [ ] **Step 4.7: Commit Phase 4**

```bash
git add backend README.md .env.example
git commit -m "feat: integrate gitlab mcp"
```

---

## Phase 5: Agent Builder And Gemini

**Files:**
- Create: `backend/services/agent_builder.py`
- Create: `backend/services/prompts.py`
- Create: `backend/tests/test_prompts.py`
- Modify: `backend/routes/brief.py`
- Modify: `backend/routes/chat.py`

- [ ] **Step 5.1: Create prompt contracts**

Brief generation prompt must require:

- exactly four sections
- concise recommendations
- source grounding
- explicit conflict detection between Notion and GitLab
- no claims that are not supported by supplied data

Chat prompt must require:

- answer the question directly
- cite GitLab activity or team guide
- return an action object instead of executing writes
- ask for confirmation before assignment

- [ ] **Step 5.2: Write prompt unit tests**

Tests should verify prompt strings mention the required brief sections, source citations, action confirmation, and GitLab write boundary.

- [ ] **Step 5.3: Wire Gemini 2.0 Flash**

Use `GEMINI_MODEL=gemini-2.0-flash` with `GEMINI_FALLBACK_MODEL=gemini-2.5-flash`. Keep all Gemini access behind `agent_builder.py` so the app can swap between deterministic fallback mode and live agent mode.

- [ ] **Step 5.4: Register tools in Agent Builder**

Register GitLab MCP and Notion access as tools in Agent Builder. This is a hackathon requirement: Agent Builder must be the orchestration layer, not just a label attached to raw Gemini calls.

- [ ] **Step 5.5: Add mode switch**

Support:

```dotenv
FLUX_AGENT_MODE=live
FLUX_AGENT_MODE=demo
```

Live mode uses Google ADK, GitLab MCP, Notion, and Gemini. Demo mode remains as deterministic fallback behavior.

- [ ] **Step 5.6: Verify live and demo paths**

Run:

```bash
cd backend
pytest tests/test_prompts.py tests/test_influence_graph.py tests/test_notion_parser.py -v
```

Then run the app in demo mode and live mode if credentials are available.

- [ ] **Step 5.7: Commit Phase 5**

```bash
git add backend README.md .env.example
git commit -m "feat: add agent builder and gemini orchestration"
```

---

## Phase 6: Action Confirmation

**Files:**
- Create: `backend/routes/action.py`
- Create: `backend/tests/test_action_confirm.py`
- Modify: `backend/main.py`
- Modify: `frontend/src/components/Chat.tsx`

- [ ] **Step 6.1: Add backend action route**

`POST /api/action/confirm` accepts:

```json
{
  "workspace_id": "abc123",
  "action": {
    "type": "assign_issue",
    "issue_id": "412",
    "project": "billing",
    "username": "newhire"
  }
}
```

It calls GitLab MCP `assign_issue` and optionally `create_issue_comment`.

- [ ] **Step 6.2: Add tests for confirmation boundary**

Tests must prove chat does not execute writes directly. Chat returns an action proposal; only confirm route executes it.

- [ ] **Step 6.3: Add frontend confirmation UI**

When chat response includes an action, show a confirm button with the issue number and target username. On click, call `/api/action/confirm` and show the returned GitLab URL.

- [ ] **Step 6.4: Verify the demo action**

In demo mode:

1. Ask: `Can you assign issue #412 to me?`
2. Confirm the UI shows a proposed action.
3. Click confirm.
4. Confirm the UI says the issue was assigned.

In live mode:

1. Use a test GitLab project and issue.
2. Confirm the assignment changes in GitLab.

- [ ] **Step 6.5: Commit Phase 6**

```bash
git add backend frontend
git commit -m "feat: add confirmed gitlab issue assignment"
```

---

## Phase 7: Frontend Demo Polish

**Files:**
- Modify: `frontend/src/pages/Setup.tsx`
- Modify: `frontend/src/pages/Onboard.tsx`
- Modify: `frontend/src/components/FluxBrief.tsx`
- Modify: `frontend/src/components/Chat.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 7.1: Make the first screen the actual app**

No marketing landing page. `/setup` is the HR setup workflow. `/onboard/{id}` is the new-hire experience.

- [ ] **Step 7.2: Polish Flux Brief**

Render four compact sections with clear evidence labels:

- Right Now
- Your People Map
- Week 1 Moves
- Landmines

Each claim should show source context, such as `GitLab, last 90 days` or `Team guide`.

- [ ] **Step 7.3: Add loading progress**

Brief generation can take 10-30 seconds. Show concrete stages:

- Reading GitLab activity
- Reading team guide
- Building influence graph
- Generating brief

- [ ] **Step 7.4: Add source attribution in chat**

Every answer should display source chips:

- GitLab activity
- Team guide
- Agent action

- [ ] **Step 7.5: Add demo question shortcuts**

Add unobtrusive buttons for the three demo questions and the action prompt:

- Who owns auth?
- How do I ship fast?
- Anything I shouldn't say in standup?
- Assign issue #412 to me

- [ ] **Step 7.6: Verify with browser QA**

Use `/browse` or an equivalent local browser test:

1. Setup form works.
2. Onboard page renders.
3. Brief fits on desktop.
4. Chat answers source labels appear.
5. Action confirmation is explicit.

- [ ] **Step 7.7: Commit Phase 7**

```bash
git add frontend
git commit -m "feat: polish flux demo experience"
```

---

## Phase 8: Docker And Cloud Run

**Files:**
- Create: `Dockerfile`
- Create: `cloudbuild.yaml` or document manual deploy in `README.md`
- Modify: `backend/main.py`
- Modify: `frontend/vite.config.ts`
- Modify: `README.md`

- [ ] **Step 8.1: Create production build flow**

Build frontend static assets and serve them from FastAPI, or use a two-service setup only if needed. Prefer one Cloud Run service for demo simplicity.

- [ ] **Step 8.2: Create Dockerfile**

Dockerfile should:

1. Build frontend with Node.
2. Install backend Python dependencies.
3. Copy built frontend assets.
4. Start Uvicorn on `$PORT`.

- [ ] **Step 8.3: Add Secret Manager values**

```bash
printf '%s' "$GITLAB_TOKEN" | gcloud secrets create flux-gitlab-token --data-file=-
printf '%s' "$NOTION_TOKEN" | gcloud secrets create flux-notion-token --data-file=-
```

If secrets already exist:

```bash
printf '%s' "$GITLAB_TOKEN" | gcloud secrets versions add flux-gitlab-token --data-file=-
printf '%s' "$NOTION_TOKEN" | gcloud secrets versions add flux-notion-token --data-file=-
```

- [ ] **Step 8.4: Deploy to Cloud Run**

```bash
gcloud run deploy flux \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=direct-subject-497307-p8,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_LOCATION=us-central1,GEMINI_MODEL=gemini-2.0-flash,GEMINI_FALLBACK_MODEL=gemini-2.5-flash,FLUX_AGENT_MODE=live,GLAB_COMMAND=glab
```

Keep `FLUX_AGENT_MODE=live` for judging now that ADK, GitLab MCP, and Notion have been verified on Cloud Run.

- [ ] **Step 8.5: Verify public URL**

Open the Cloud Run URL and complete the demo flow from a clean browser session.

- [ ] **Step 8.6: Commit Phase 8**

```bash
git add Dockerfile README.md cloudbuild.yaml backend frontend
git commit -m "chore: add cloud run deployment"
```

---

## Phase 9: Submission Assets

**Files:**
- Create: `docs/demo-script.md`
- Create: `docs/submission-checklist.md`
- Modify: `README.md`

- [ ] **Step 9.1: Write demo script**

Use this exact 3-minute structure:

- 0:00-0:25: stale onboarding PDF problem
- 0:25-0:45: HR setup
- 0:45-1:15: generated Flux Brief
- 1:15-2:30: three live questions
- 2:30-2:50: assign issue #412 action
- 2:50-3:00: close

- [ ] **Step 9.2: Record demo video**

Record in live mode. The product should visibly use the GitLab MCP and Agent Builder/ADK architecture in README and, if possible, live logs.

- [ ] **Step 9.3: Create submission checklist**

Checklist:

- Hosted Cloud Run URL
- Public GitHub repo
- MIT license
- README setup instructions
- Demo video under 3 minutes
- GitLab partner track selected
- Clear mention of Google Cloud Agent Builder
- Clear mention of Gemini 2.0 Flash
- Clear mention of GitLab MCP read and write operations

- [ ] **Step 9.4: Final smoke test**

From the public URL:

1. Setup link generation works.
2. Brief generates.
3. Three demo questions answer correctly.
4. Action confirmation works.
5. No secrets appear in browser devtools, logs, README, or repo history.

- [ ] **Step 9.5: Commit Phase 9**

```bash
git add docs README.md
git commit -m "docs: add flux submission assets"
```

---

## Risk Register

| Risk | Mitigation |
|---|---|
| Agent Builder/ADK setup regresses | Keep deterministic fallback mode, but record the current live ADK/MCP deployment first. |
| GitLab MCP write action is hard to wire | Build the confirmation boundary first; use a test GitLab project and issue. |
| Notion auth is flaky | Keep demo markdown fallback and show source label as demo/team guide. |
| Cloud Run deployment eats time | Use a single service and deploy demo mode first. |
| Scope creep into SaaS product | Do not build accounts, DB, scheduling, mobile, HRIS, or persistent memory. |
| Credit not redeemed in time | Redeem Google Cloud credit before any deployment work. |

## Definition Of Done

Flux is done for hackathon submission when:

- A judge can open a Cloud Run URL.
- HR setup produces a new-hire link.
- New-hire page generates a four-section Flux Brief.
- Chat answers the required demo questions with source attribution.
- The app proposes assigning issue `#412` and executes it only after confirmation.
- README explains Google Cloud Agent Builder, Gemini 2.0 Flash, GitLab MCP, Notion, and Cloud Run setup.
- Repo is public and MIT licensed.
- Demo video is under 3 minutes.
