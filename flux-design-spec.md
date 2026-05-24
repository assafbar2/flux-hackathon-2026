# Flux — Design Spec

**Date:** 2026-05-07
**Tagline:** The org as it runs, not as it's drawn.
**Hackathon:** Google Cloud Rapid Agent Hackathon
**Partner track:** GitLab
**Status:** Approved for implementation planning

---

## 1. Problem

Engineers starting a new job get a PDF. It was written 8 months ago by someone who's since left. It tells them the org chart, the official process, and which Confluence page to read first.

None of that tells them:
- Who actually reviews the code they'll be touching
- What's on fire right now and what to stay away from
- Which senior engineer is unavailable until June
- What you should never say in standup (and why)
- Which docs are stale vs. which are live

The result: 60–90 days before a new engineer is genuinely productive. Not because they're slow — because they spent 3 weeks learning the wrong org.

**Flux fixes that on day one.**

---

## 2. What Flux Is

Flux is an onboarding intelligence agent for engineers at SaaS companies. It reads two data sources — GitLab activity and a HR-maintained Notion page — and answers questions that no org chart ever could.

**Target user:** New engineer, day 1–30, at a SaaS company with a GitLab-based eng workflow.
**Distribution:** B2D (direct to engineer). HR provisions the workspace; the engineer drives.
**Format:** Web app — chat interface with an initial generated Flux Brief.

---

## 3. Two Roles

### HR Admin (sets up once, before new hire starts)

1. Opens Flux and connects their GitLab org with a read-only token (GitLab personal access token, `read_api` scope)
2. Pastes their Notion "team intelligence" page URL into Flux
3. Sends the new hire a provisioned Flux link

Time investment: ~10 minutes. Done once per hire.

### New Engineer (day 1)

1. Opens their Flux link — no account creation required
2. Flux agent reads 90 days of GitLab activity + the Notion page
3. A **Flux Brief** is generated automatically
4. Chat interface opens for ongoing questions throughout onboarding

---

## 4. Data Sources

### GitLab (via GitLab MCP — partner integration)

The agent pulls via the GitLab MCP server:

- **Commits:** author, repo, frequency, recency — establishes who owns what by actual work
- **Merge requests:** who creates them, who reviews them, how long reviews take per reviewer
- **Code reviews:** reviewer patterns per repo — the single most reliable signal for real ownership
- **Issues:** open P1s and P0s, issue labels, assignees — surfaces active fires
- **Repo metadata:** last activity per repo, contributor count — identifies bus factor and active vs. abandoned codebases

What Gemini does with this: builds an **influence graph** — a map of who actually owns each area of the codebase, derived from review patterns rather than job titles.

### Notion (via Notion public API)

HR pre-populates a Flux-provided Notion template before the hire's start date. The page is structured in four sections:

**The Team (Real Talk)**
One entry per team member. Not just name/role — also:
- Availability patterns (e.g., "offline Fridays after 4pm")
- Real ownership vs. nominal title
- Current bandwidth situation
- Best way to reach them / ideal first interaction

**Right Now**
What's actually happening this sprint/month:
- Active crunch projects (and how long until they're done)
- Known blockers and who owns them
- Safe areas for new hire contributions
- Anything that's politically sensitive right now

**Unwritten Rules**
The stuff that never makes it into handbooks:
- Topics to avoid in public channels
- Deploy norms (e.g., "no Friday deploys without a +1 from X")
- Which Slack channels are actually used vs. performative
- How decisions really get made (vs. how the process doc says they do)

**How to Ship**
Tactical, specific:
- Who to tag for fast reviews (and their typical turnaround)
- PR template requirements
- Any gotchas in the deploy pipeline
- What "done" means on this team

---

## 5. The Flux Brief

Generated automatically when a new hire first opens their link. Not a scheduled push — a one-time, on-connect synthesis. Four sections:

### 🔥 Right Now
What's active and what to avoid this week. Sourced from GitLab open P1 issues cross-referenced with Notion's "Right Now" section. Example output: *"The SSO migration is a live P1. Marcus owns it and is blocked on a vendor response. Don't touch the auth module this week."*

### 🧭 Your People Map
Who owns what, derived from data not org charts. Top 3–5 people the new hire should know, with evidence. Example output: *"Marcus reviewed 71% of auth PRs in the last 90 days. He's listed as a senior engineer but he's the de facto owner. Best first coffee — Notion says he responds fast and is welcoming to new hires."*

### ⚡ Week 1 Moves
Three specific, actionable things to do in the first week. Sourced from GitLab good-first issues + Notion safe contribution zones. Example output: *"Billing module has 3 open good-first issues. It's one of the stable areas right now. Issue #412 has no assignee and a clear spec."*

### 🚧 Landmines
What not to say, break, or assume. Sourced entirely from Notion's "Unwritten Rules." Example output: *"Don't ask why the team didn't use GraphQL — there's history. Friday deploys need sign-off from Marcus or Dev. #eng-general is read by the CEO; real conversations happen in #eng-real."*

---

## 6. Chat Interface

After the Flux Brief, the new hire can ask anything. The agent answers using both data sources, always citing which source informed the answer.

**Representative demo questions and expected answer shape:**

| Question | Sources used | Answer shape |
|---|---|---|
| "Who actually owns the auth system?" | GitLab review data + Notion people | Names Marcus with evidence (71% of auth PRs), cross-checks Notion |
| "Who should I avoid pinging right now?" | Notion bandwidth + GitLab activity drop | Sarah (parental leave until June 15) + Priya (80% on migration) |
| "What should I work on in week 1?" | GitLab open issues + Notion safe zones | Specific issue numbers in billing/notifications |
| "How do I get a PR merged fast?" | GitLab review turnaround + Notion ship guide | Tag Marcus, follow template, no Friday deploys |
| "Which meetings actually matter?" | Notion meeting culture section | Thursday 1:1 is real; Tuesday standup is performative |
| "Anything I shouldn't say in standup?" | Notion unwritten rules | GraphQL history, CEO reads #eng-general |
| "What's the fastest way to understand this codebase?" | GitLab high-churn files + top contributors | 3 files, 2 people to talk to, 1 active thread |
| "Is there anything politically sensitive right now?" | Notion current reality | SSO migration contention, v1→v2 debate |
| "Can you assign issue #412 to me?" | GitLab MCP write | **Takes action** — assigns the issue, posts a comment, confirms back |

Answers always ground claims in evidence: *"According to GitLab data from the last 90 days..."* or *"Per the team guide HR set up..."*

---

## 7. Technical Architecture

### Stack

| Layer | Technology |
|---|---|
| Agent orchestration | Google Cloud Agent Builder |
| LLM | Gemini 2.0 Flash |
| Partner integration | GitLab MCP (official partner MCP server) |
| Team context | Notion public API |
| Frontend | React (single page, minimal) |
| Hosting | Google Cloud Run |

### Agent workflow

```
New hire opens Flux link
  │
  ├── Agent calls GitLab MCP
  │     ├── List repos (last active 90 days)
  │     ├── Fetch commits per repo (author, date)
  │     ├── Fetch MRs (author, reviewers, merge time)
  │     └── Fetch open issues (P1/P0 labels, assignees)
  │
  ├── Agent calls Notion API
  │     └── Read page content (4 sections as structured text)
  │
  ├── Gemini 2.0 Flash synthesizes
  │     ├── Builds influence graph (reviewer patterns → real ownership)
  │     ├── Cross-references GitLab signals with Notion context
  │     └── Generates Flux Brief (4 sections)
  │
  └── Returns to frontend
        ├── Renders Flux Brief
        ├── Opens chat (agent retains context for follow-up questions)
        └── On action confirmation → Agent calls GitLab MCP (write)
              ├── assign_issue: assigns recommended issue to new hire
              └── create_issue_comment: optional "starting this" comment
```

### Google Cloud Agent Builder — specific role

Agent Builder is the orchestration layer, not a label we attach to raw Gemini calls. It handles:

- **Tool definitions:** GitLab MCP and Notion API are registered as callable tools in Agent Builder. The agent decides which tools to call and in what order — it is not hardcoded.
- **Multi-turn grounding:** the conversation history (Flux Brief + chat) stays in Agent Builder's session context, so each chat message doesn't require re-fetching all data.
- **Safety settings:** Agent Builder's content filters are configured to prevent PII leakage (no surfacing of private HR data beyond what the Notion page contains).
- **Action confirmation:** when the agent proposes a write action (issue assignment), Agent Builder handles the human-in-the-loop confirmation step before executing.

### GitLab MCP — specific calls

**Read operations (brief generation):**
- `list_projects` — get all repos the token has access to
- `list_commits` — per repo, last 90 days, grouped by author
- `list_merge_requests` — per repo, last 90 days, with reviewer data
- `list_issues` — open issues filtered by P1/P0 labels or unassigned good-first-issue tags

**Write operations (agent actions — user confirms before execution):**
- `assign_issue` — assign a recommended good-first issue to the new hire's GitLab username
- `create_issue_comment` — optionally post a "starting work on this" comment on the assigned issue

These write actions are what satisfy the hackathon's "Move Beyond Chat" requirement. The agent doesn't just surface good-first issues — it can assign them, turning intelligence into action with one confirmation click.

### Notion — specific calls

Single Notion API call: `GET /v1/blocks/{page_id}/children` with recursive expansion to retrieve all page content. Parsed into the four named sections before passing to Gemini.

### What Gemini is doing (not just retrieval)

The intelligence layer is where Flux earns its demo moment. Gemini is not running keyword search — it is:

1. **Building the influence graph:** For each repo, calculate review contribution % per person. Flag where the nominal lead and the actual reviewer diverge.
2. **Freshness scoring:** Cross-check Notion content against GitLab activity dates. If a doc mentions a person who hasn't committed in 6 months, flag it.
3. **Conflict detection:** If Notion says Sarah owns auth but GitLab shows Marcus reviewing 70% of auth PRs, surface the delta explicitly.
4. **Synthesis:** Combine quantitative GitLab signals with qualitative Notion context to produce answers that neither source could produce alone.

---

## 8. Notion Template Structure

HR fills this in before the hire's start date. Flux provides the template as a Notion page the HR admin can duplicate.

```
# [Company] Team Intelligence — Flux

## The Team (Real Talk)
### [Name]
- Role: [official title]
- Real ownership: [what they actually do / own]
- Availability: [patterns, time zones, known constraints]
- Best way to engage: [Slack / async / quick syncs / etc.]
- Current bandwidth: [available / heads-down / on leave until X]

## Right Now (updated [date])
- **Active crunch:** [project name] — [context, who's on it, when it ends]
- **Live blockers:** [what's stuck and who owns it]
- **Safe zones for new hires:** [areas with low blast radius, good first issues]
- **Politically sensitive:** [anything to be aware of]

## Unwritten Rules
- [Rule 1]
- [Rule 2]
- [Rule 3]

## How to Ship Here
- **Fastest reviewer:** [name] — avg [X]hr turnaround
- **PR requirements:** [template, checklist, etc.]
- **Deploy rules:** [when, who needs to sign off]
- **Gotchas:** [anything that trips people up]
```

---

## 9. Scope (Hackathon Build)

### In scope

- HR setup flow (GitLab token input + Notion URL input)
- New hire link generation (unique URL per hire, encodes GitLab org + Notion page ID, no auth required to open)
- GitLab data ingestion via MCP
- Notion page ingestion via API
- Flux Brief generation (4 sections)
- Chat interface with grounded Q&A
- Hosted on Google Cloud Run

### Explicitly out of scope for hackathon

- Daily brief scheduling / push notifications
- User accounts / authentication
- Persistent memory across sessions
- Fivetran / HRIS integration
- Elastic RAG layer
- Multi-company support
- Mobile

---

## 10. Judging Criteria Mapping

| Criterion | How Flux addresses it |
|---|---|
| **Technological implementation** | GitLab MCP + Gemini 2.0 Flash + Cloud Agent Builder. Agent makes multi-step tool calls (read AND write to GitLab), synthesizes across two sources, produces structured output, and takes real-world actions. Not a wrapper. |
| **Design** | Two clear roles (HR, new hire). Zero-friction new hire flow (no account). Flux Brief as the first-load experience — immediate value before any interaction. |
| **Potential impact** | GitLab has 30M+ users across 50K+ organizations. Every engineering team that hires is a target. Time-to-productivity improvement from 60–90 days to 2 weeks is a measurable, documented outcome — and the cost of a slow ramp (salary + management overhead) is typically $15–30K per hire. |
| **Quality of idea** | Nobody has built this. Prediction markets exist. Onboarding docs exist. An agent that reads the actual work and tells you the real org — that doesn't exist yet. |

---

## 11. Demo Script (3 minutes)

**0:00–0:25 — The problem**
Show a generic onboarding PDF. "Last updated 8 months ago. David is listed as the auth lead. David left the company 3 months ago."

**0:25–0:45 — The setup**
HR view: GitLab token + Notion URL. Two fields. Done. "This takes 10 minutes. You do it once."

**0:45–1:15 — The Flux Brief**
New hire opens their link. Brief generates live. Walk through all four sections. Highlight the delta: "The org chart says Priya owns auth. GitLab says Marcus reviewed 71% of auth PRs. Flux shows you both — and tells you what it means."

**1:15–2:45 — Three questions + one action**
1. *"Who should I talk to about the auth system?"* — Marcus, with evidence
2. *"How do I ship my first PR without making enemies?"* — tag Marcus, use the template, no Friday deploys, here's why
3. *"Anything I shouldn't say in standup?"* — yes, three things, sourced from Notion
4. **[The action]** *"Can you assign issue #412 to me?"* — agent confirms, calls GitLab MCP, issue is assigned live on screen. "Done — issue #412 is now yours."

**2:45–3:00 — The close**
"Every engineer deserves this on day one. Not a PDF. Not a wiki. The real org — and a first task already assigned."

---

*Spec written by Claude Sonnet 4.6 via Flux brainstorming session, 2026-05-07.*
