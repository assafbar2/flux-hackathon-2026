# Flux Demo Script

Target length: 2:45 to 3:00.

## Setup Before Recording

- Open the live app: https://flux-153593352872.us-central1.run.app
- Open the GitLab issue list in another tab.
- Keep the Notion team guide available if you want to show the HR-maintained source.
- Use blank setup fields unless you specifically want to show the token flow. Blank fields are safer for video because the deployed service already has Secret Manager configuration.
- If issue `#412` is already assigned, unassign it before recording or say "Flux can assign it live" and show the confirmed result.

## The Story

Flux replaces stale onboarding docs with a live day-one agent. It reads what the team actually does in GitLab, combines it with the HR-maintained Notion guide, and turns that into a new-hire brief plus a first real action.

## Timeline

### 0:00-0:40 — The Problem

Say:

> Every month, 4 million people start a new job. In tech, 26 million engineers work across hundreds of thousands of engineering teams — and almost every one of them goes through the same broken ritual on day one: a PDF, a stale wiki, and a manager who says "just ask around."
>
> The problem isn't the new hire. The problem is that the onboarding doc was written 8 months ago by someone who's since left. It shows you the org chart. It doesn't tell you who actually reviews the auth code, what's on fire this week, or why you should never ask about GraphQL in standup.
>
> The result: it takes the average engineer 60 to 90 days to become genuinely productive. That's $20,000 in salary and management time per hire — before they ship a single line of code that matters.
>
> There's also a trust problem. New hires who feel lost in week one disengage. Teams that invest in a great first day retain people longer and ramp them faster. And teams that show up with AI-powered tooling on day one — not buried in an onboarding doc, but live and answering real questions — signal something important: we are an AI-first team. That matters for recruiting, for retention, and for the kind of engineers you attract.
>
> Flux fixes this. Not with a better template. With a live agent that reads the actual work — and tells the new hire the real org, not the drawn one.

Optional visual:

- Show a stale onboarding PDF or the Flux landing page while speaking.

### 0:40-0:55 — HR Setup

Action:

1. Show the Flux setup page.
2. Leave the fields blank for demo mode.
3. Click `Generate link`.
4. Open the generated onboarding link.

Say:

> HR only needs a GitLab token and a Notion team guide URL. For this demo, the production service already has secure server-side configuration, so I can generate a new-hire link without putting secrets in the browser. Behind this page, Flux runs on Cloud Run and orchestrates Gemini through Google Cloud Agent Builder — using the ADK Python SDK — with GitLab MCP tools.

### 0:55-1:25 — The Flux Brief

Action:

Scroll the four brief sections.

Say:

> This is the day-one brief. It tells the new hire what is active right now, who actually owns key systems, what to work on in week one, and what unwritten rules could hurt them if they learn them too late.

Call out:

- `Right Now`: SSO migration is a live P1.
- `Your People Map`: Marcus is the de facto auth owner based on review share.
- `Week 1 Moves`: billing and notifications are safe first areas.
- `Landmines`: GraphQL and Friday deploys are sensitive.

### 1:25-2:15 — Grounded Questions

Ask these using the prompt buttons or chat box:

```text
Who owns auth?
```

Say:

> Flux does not answer from the org chart. It cites GitLab MCP data and the team guide.

Ask:

```text
How do I ship fast?
```

Say:

> This combines live GitLab MCP data with the team's written and unwritten shipping rules.

Ask:

```text
Anything I shouldn't say in standup?
```

Say:

> This is the kind of onboarding knowledge that rarely appears in official docs but matters immediately.

### 2:15-2:50 — The Action Moment

Ask:

```text
Assign issue #412 to me
```

Action:

1. Wait for Flux to propose the assignment.
2. Click `Confirm assignment`.
3. Show the success message.
4. Switch to GitLab and show the issue assignment if available.

Say:

> Flux moves beyond chat. It proposes a concrete first task, asks for confirmation, and then writes back to GitLab through the GitLab MCP server.

### 2:50-3:00 — Close

Say:

> Every engineer deserves this on day one: not a PDF, not a stale org chart, but the real team context and a first task already assigned.

## Backup Lines

If the GitLab write is already assigned:

> The live action path is connected. This issue is already assigned from a previous run, which is what we expect after a successful demo.

If Notion is slow:

> Flux has deterministic fallback data for demo reliability, but the deployed service is configured to read the live Notion team guide when available.

If asked about Agent Builder:

> The deployed build routes brief and chat generation through Google ADK with Gemini, and exposes GitLab through the official GitLab CLI MCP server. Gemini 2.0 Flash is configured as primary with a Gemini 2.5 Flash fallback because this project currently cannot access the 2.0 Flash model in the tested Vertex locations.
