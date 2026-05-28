# Flux — Agent Instructions

You are building **Flux**, a hackathon project for the Google Cloud Rapid Agent Hackathon (deadline: June 11, 2026).

Read this entire file before writing a single line of code. Everything you need to make good decisions is here.

---

## Current Implementation Status

Read this before using the rest of this file as a plan.

- Live app: https://flux-153593352872.us-central1.run.app
- Devpost submission: https://devpost.com/software/flux-veocby
- Cloud Run service: `flux`, region `us-central1`, project `direct-subject-497307-p8`
- Current deployed mode: `FLUX_AGENT_MODE=live`
- Public access is enabled with `allUsers -> Cloud Run Invoker` on the `flux` service.
- Notion ingestion is live when configured and falls back to `backend/demo_data/notion_page.md`.
- GitLab issue reads and confirmed assignment are live through the official GitLab CLI MCP server (`glab mcp serve`).
- Brief and chat synthesis route through Google ADK (`LlmAgent` + `Runner`) with Gemini.
- `GEMINI_MODEL=gemini-2.0-flash` is configured as primary with `GEMINI_FALLBACK_MODEL=gemini-2.5-flash` because this project currently returns Vertex 404s for Gemini 2.0 Flash in tested locations.
- Judge-facing docs live in `README.md`, `docs/DEMO_SCRIPT.md`, `docs/DEVPOST_SUBMISSION.md`, `docs/AGENT_BUILDER_PROOF.md`, `docs/ROADMAP.md`, and `docs/submission-checklist.md`.

The rest of this file is the product and architecture target. Treat any conflicts in favor of the current status above plus the latest code.

---

## What Flux Is

**Tagline:** The org as it runs, not as it's drawn.

Flux is an onboarding intelligence agent for engineers joining any team that runs on GitLab. It answers questions on day one that no onboarding doc ever could — because it reads the actual work history, not the org chart. Then it acts: it can assign good-first issues directly to the new hire via GitLab, turning intelligence into a real first task.

**The core problem:** New engineers get a PDF. It was written 8 months ago. It tells them the official org chart and links to a Confluence page nobody updates. It doesn't tell them who actually reviews the auth code, what's on fire right now, or why they should never ask about GraphQL in standup.

**The solution:** Flux reads two data sources — 90 days of GitLab activity and a HR-maintained Notion page — and generates a "Flux Brief" plus a chat interface. The new engineer gets real intelligence on day one.

---

## Two Users, One System

### User 1: HR Admin (sets up once, before the hire starts)
1. Opens Flux and enters a GitLab personal access token (read-only, `read_api` scope) for the org
2. Pastes the URL of their Notion "team intelligence" page
3. Clicks "Generate link" — gets a unique URL to send to the new hire

**HR time investment: ~10 minutes. Done once per hire.**

### User 2: New Engineer (day 1)
1. Opens their Flux link — no account, no login
2. Sees a loading state while the agent runs (reads GitLab + Notion)
3. The **Flux Brief** appears automatically (4 sections — see below)
4. Chat interface opens for ongoing questions

---

## Data Sources

### GitLab (via GitLab MCP — the hackathon partner integration)

The agent calls the GitLab MCP server to fetch:
- **Projects/repos:** all repos the token can access, filtered to those with activity in the last 90 days
- **Commits:** per repo, last 90 days, grouped by author — establishes who actually works on what
- **Merge requests:** per repo, last 90 days — who creates them, who reviews them, how long reviews take per reviewer
- **Code reviews (MR approvals/comments):** the single most reliable signal for real ownership — whoever reviews the most PRs in an area owns that area, regardless of their title
- **Issues:** open issues with P1/P0 labels and assignees — surfaces active fires

**What Gemini does with this data:** builds an influence graph. For each repo and major directory, it calculates who is the actual owner by review contribution %, not job title. It identifies where the nominal lead and the actual reviewer diverge — that delta is the insight.

### Notion (via Notion public API)

HR pre-populates a Notion page from a template Flux provides. The page has four sections:

```
## The Team (Real Talk)
One entry per person:
- Official role
- What they actually own / do (vs. title)
- Availability patterns (e.g., "offline Fridays after 4pm for school pickup")
- Current bandwidth: available / heads-down / on leave until [date]
- Best way to engage

## Right Now (updated [date])
- Active crunch projects and when they end
- Live P1 blockers and who owns them
- Safe zones for new hire contributions (low blast radius)
- Anything politically sensitive right now

## Unwritten Rules
- Topics to avoid in public channels and why
- Deploy norms (e.g., "no Friday deploys without +1 from Marcus or Dev")
- Which Slack channels are real vs. performative
- How decisions actually get made (vs. the process doc)

## How to Ship Here
- Fastest reviewer and their turnaround time
- PR template requirements
- Deploy pipeline gotchas
- What "done" means on this team
```

---

## The Flux Brief

Generated automatically on first load. Four sections:

**🔥 Right Now**
What's active and what to avoid this week. Cross-references GitLab open P1 issues with Notion's "Right Now" section. Example: *"The SSO migration is a live P1. Marcus owns it and is blocked on a vendor response. Don't touch the auth module this week."*

**🧭 Your People Map**
Top 3–5 people the new hire needs to know, derived from data not org charts. Shows evidence. Example: *"Marcus reviewed 71% of auth PRs in the last 90 days. He's the de facto owner, not just a senior engineer. Notion says he's welcoming to new hires and responds fast."*

**⚡ Week 1 Moves**
Three specific, actionable things to do in week 1. Example: *"Billing module has 3 open good-first issues. It's a stable area right now. Issue #412 has no assignee and a clear spec — good first PR."*

**🚧 Landmines**
What not to say, break, or assume. Sourced from Notion's "Unwritten Rules" only. Example: *"Don't ask why the team didn't use GraphQL — there's history. Friday deploys need sign-off from Marcus or Dev. #eng-general is read by the CEO."*

---

## Demo Questions the Chat Must Answer Well

These 7 questions are the demo. The agent must answer them grounded in actual GitLab data + Notion content:

1. **"Who actually owns the auth system?"** → not the person on the org chart, the person who reviews auth PRs
2. **"Who should I avoid pinging right now?"** → people on leave or heads-down (from Notion + low GitLab activity)
3. **"What should I work on to make an impact in week 1?"** → safe zones from Notion + good-first issues from GitLab
4. **"Is there anything I shouldn't say in standup?"** → Notion unwritten rules
5. **"How do I get a PR merged fast?"** → fastest reviewer from GitLab data + PR norms from Notion
6. **"Which meetings actually matter?"** → Notion meeting culture section
7. **"What's the fastest way to understand this codebase?"** → highest-churn files from GitLab + top contributors

Every answer should cite its source: *"Based on GitLab activity over the last 90 days..."* or *"Per the team guide..."*

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Agent orchestration | Google Cloud Agent Builder | Required by hackathon — registers GitLab MCP + Notion as tools, manages multi-turn context, handles action confirmation |
| LLM | Gemini 2.0 Flash | Required by hackathon |
| Partner integration | GitLab MCP (official partner MCP server) | Required for GitLab prize track — both read AND write operations |
| Team context | Notion public API (`/v1/blocks/{id}/children`) | Simple read, no auth complexity |
| Frontend | React + TypeScript + Vite | Fast to build, easy to host |
| Backend/API | FastAPI (Python) | Serves the API and built frontend from one Cloud Run service |
| Hosting | Google Cloud Run | Required by hackathon, $100 credit available |
| License | MIT (required by hackathon) |  |

**Google Cloud credit:** $100 credit is available for Cloud Run, Secret Manager, and Vertex/Gemini usage during the hackathon.

---

## Architecture

```
[HR Admin UI]
  ├── Enter GitLab token (read_api scope)
  ├── Enter Notion page URL
  └── → POST /api/setup → returns {workspace_id, hire_link}

[New Hire opens /onboard/{workspace_id}]
  └── GET /api/brief/{workspace_id}
        ├── GitLab MCP: fetch repos, commits, MRs, issues (last 90 days)
        ├── Notion API: GET /v1/blocks/{page_id}/children (recursive)
        ├── Gemini: synthesize → build influence graph + Flux Brief
        └── returns {brief: {now, people, moves, landmines}, context: [...]}

[Chat]
  └── POST /api/chat
        ├── message: user's question
        ├── workspace_id: to reload context if needed
        ├── Agent Builder: routes to GitLab MCP or Notion based on question
        └── returns {answer, sources: ["gitlab"|"notion"], action?: {type, payload}}

[Action confirmation — when agent proposes a write]
  └── POST /api/action/confirm
        ├── action: {type: "assign_issue", issue_id, username}
        ├── Agent Builder: calls GitLab MCP assign_issue tool
        └── returns {success, gitlab_url}
```

**Important:** The context (GitLab data + Notion page) is fetched once when the brief is generated and stored in memory or a simple cache for the session. Don't re-fetch on every chat message.

---

## Current Build

Implemented:

1. React + TypeScript setup and onboarding flows.
2. FastAPI routes for setup, brief generation, chat, action proposal, action confirmation, and health.
3. Notion ingestion with deterministic fallback data for judge reliability.
4. GitLab MCP issue reads and confirmed issue assignment through `glab mcp serve`.
5. Google ADK `LlmAgent` + `Runner` orchestration with Gemini and GitLab MCP registered as a toolset.
6. Explicit confirmation UI before any GitLab write.
7. Cloud Run deployment with Secret Manager wiring.
8. Public README, demo video, submission draft, roadmap, and proof notes.

Submitted to Devpost on May 28, 2026. Remaining work is post-submission maintenance only unless a judge or organizer requests a change.

---

## Scope — What NOT to Build

Do not build any of these. They are out of scope for the hackathon:

- User accounts or authentication (the hire link IS the auth)
- Daily brief scheduling or push notifications
- Persistent memory across sessions (in-memory cache is fine for the demo)
- Fivetran or HRIS integration (Notion IS the HRIS for this demo)
- Elastic or any RAG layer beyond Notion + GitLab
- Multi-company support (one workspace per Flux instance is fine)
- Mobile responsiveness (desktop only for the hackathon)
- Any database (file-based or in-memory storage for the demo is acceptable)

---

## The Notion Demo Page

For the hackathon demo, HR has already filled in a Notion page. The agent reads it at runtime. The page content looks like this (you'll use this as test data):

```
## The Team (Real Talk)

### Marcus Chen — Senior Engineer
- Real ownership: Auth system, payments integration (reviews 70%+ of PRs in these areas)
- Availability: Offline Fridays after 4pm (school pickup). Back on Slack by 8pm.
- Bandwidth: Available — good time to connect
- Best way: Slack DM first, then schedule a 30min pairing session

### Sarah Kim — Staff Engineer / Architect
- Real ownership: System architecture, data model decisions
- Availability: On parental leave until June 15, 2026
- Bandwidth: Unavailable until June 15
- Best way: Don't ping her until she's back. Talk to Dev instead.

### Priya Patel — Engineering Lead (nominal)
- Real ownership: Team process, roadmap, 1:1s
- Availability: Normal hours, but 80% focused on enterprise migration until Q3
- Bandwidth: Limited for new hire unblocking — go to Marcus
- Best way: Thursday 1:1 is the right venue for anything strategic

### Dev Sharma — Senior Engineer
- Real ownership: Infrastructure, CI/CD pipeline, deploy process
- Availability: Standard hours
- Bandwidth: Available
- Best way: #eng-infra channel for infra questions, DM for urgent

## Right Now (updated May 2026)

- **Active crunch:** Project Atlas (frontend rewrite) — ends May 30. Don't book frontend eng time until June.
- **Live P1:** SSO migration — Marcus owns it, blocked on Okta vendor response. ETA unknown. Don't touch /auth module.
- **Safe zones for new hires:** billing module, notifications service, docs improvements
- **Good first issues:** billing/#412 (no assignee, clear spec), notifications/#89 (small feature, well-scoped)
- **Politically sensitive:** The v1→v2 API migration has been contentious. Don't ask why we didn't do it differently.

## Unwritten Rules

- Don't ask "why didn't you use GraphQL?" in public — there's a 2-year history, you don't want to open it
- Friday deploys require explicit +1 from Marcus OR Dev. No exceptions, even hotfixes.
- #eng-general is read by the CEO and investors. Real technical conversations happen in #eng-real.
- Tuesday standup is performative and goes on Loom. The actual team sync is Thursday's eng retro.
- PR template is mandatory. Skip it and it gets returned without review, no exceptions.
- We don't do code ownership files — but Marcus/auth and Dev/infra are the de facto owners.

## How to Ship Here

- **Fastest reviewer:** Marcus — average 2hr turnaround on auth/payments PRs. Tag him.
- **Second fastest:** Dev — average 4hr for infra/backend PRs.
- **PR template:** Use it. Check all the boxes. If a box doesn't apply, strike it out don't delete it.
- **Friday rule:** No deploys on Fridays without +1 from Marcus or Dev. Even small ones.
- **Deploy process:** merge to main → CI runs → auto-deploys to staging → manual promote to prod (Dev owns this)
- **Definition of done:** PR merged + staging verified + ticket closed + #eng-shipping message posted
```

---

## Hackathon Submission Requirements

When the project is ready to submit:

1. **Hosted URL:** Deploy to Cloud Run, get a public URL
2. **GitHub repo:** Public, MIT license visible in README, clear setup instructions
3. **Demo video:** Under 3 minutes, hosted at https://youtu.be/oIAdQKI1Kek. Final script lives in `docs/DEMO_SCRIPT.md`.
4. **Partner track:** GitLab

---

## File Structure to Build

```
/
├── AGENTS.md              ← this file
├── README.md              ← setup instructions for judges
├── LICENSE                ← MIT
├── Dockerfile
├── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Setup.tsx       ← HR admin flow
│   │   │   └── Onboard.tsx     ← new hire flow (brief + chat)
│   │   ├── components/
│   │   │   ├── FluxBrief.tsx   ← 4-section brief display
│   │   │   └── Chat.tsx        ← chat interface
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── main.py                 ← FastAPI app
│   ├── routes/
│   │   ├── setup.py            ← POST /api/setup
│   │   ├── brief.py            ← GET /api/brief/{id}
│   │   └── chat.py             ← POST /api/chat
│   ├── services/
│   │   ├── gitlab_mcp.py       ← GitLab MCP client
│   │   ├── notion.py           ← Notion API client
│   │   ├── gemini.py           ← Gemini + Agent Builder client
│   │   └── influence_graph.py  ← GitLab data → real org map
│   └── requirements.txt
└── docs/
    ├── flux-design-spec.md   ← full design spec
    ├── DEMO_SCRIPT.md        ← final hosted video script
    ├── ROADMAP.md            ← next-step roadmap
    └── AGENT_BUILDER_PROOF.md
```

---

## How to Continue

1. Read `docs/flux-design-spec.md` for the original design rationale.
2. Read `docs/DEMO_SCRIPT.md` and `docs/DEVPOST_SUBMISSION.md` before changing public-facing copy.
3. Keep the Cloud Run, ADK, Gemini, GitLab MCP, and Notion architecture intact.
4. Preserve the blank-field judge flow and explicit confirmation before any GitLab write.

**When in doubt:** ship something that demos well over something that's architected perfectly. This is a 19-day hackathon.

---

## Key Constraints

- **Google Cloud Agent Builder is required** — use it as the orchestration layer, not just raw Gemini API calls
- **GitLab MCP is required** — use the official GitLab MCP server, not raw GitLab REST API calls
- **Must be hosted** — judges will click the link. Cloud Run is the target.
- **Must be open source** — MIT license, public repo, setup instructions a judge can follow
- **Demo video under 3 minutes** — plan for it from the start

---

*Project spec: docs/flux-design-spec.md*
*Hackathon: Google Cloud Rapid Agent Hackathon — deadline June 11, 2026*
*Partner track: GitLab*
