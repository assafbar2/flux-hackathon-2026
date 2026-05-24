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

### 0:00-0:20 — The Problem

Say:

> Most onboarding tells a new engineer the official org chart. That is almost never how the team actually works. Flux shows the org as it runs: who owns what, what is on fire, what not to touch, and where a new hire can safely make their first contribution.

Optional visual:

- Show a stale onboarding doc or just stay on the Flux landing page.

### 0:20-0:40 — HR Setup

Action:

1. Show the Flux setup page.
2. Leave the fields blank for demo mode.
3. Click `Generate link`.
4. Open the generated onboarding link.

Say:

> HR only needs a GitLab token and a Notion team guide URL. For this demo, the production service already has secure server-side configuration, so I can generate a new-hire link without putting secrets in the browser. Behind this page, Flux runs on Cloud Run and orchestrates Gemini through Google ADK with GitLab MCP tools.

### 0:40-1:15 — The Flux Brief

Action:

Scroll the four brief sections.

Say:

> This is the day-one brief. It tells the new hire what is active right now, who actually owns key systems, what to work on in week one, and what unwritten rules could hurt them if they learn them too late.

Call out:

- `Right Now`: SSO migration is a live P1.
- `Your People Map`: Marcus is the de facto auth owner based on review share.
- `Week 1 Moves`: billing and notifications are safe first areas.
- `Landmines`: GraphQL and Friday deploys are sensitive.

### 1:15-2:05 — Grounded Questions

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

### 2:05-2:45 — The Action Moment

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

### 2:45-3:00 — Close

Say:

> Every engineer deserves this on day one: not a PDF, not a stale org chart, but the real team context and a first task already assigned.

## Backup Lines

If the GitLab write is already assigned:

> The live action path is connected. This issue is already assigned from a previous run, which is what we expect after a successful demo.

If Notion is slow:

> Flux has deterministic fallback data for demo reliability, but the deployed service is configured to read the live Notion team guide when available.

If asked about Agent Builder:

> The deployed build routes brief and chat generation through Google ADK with Gemini, and exposes GitLab through the official GitLab CLI MCP server. Gemini 2.0 Flash is configured as primary with a Gemini 2.5 Flash fallback because this project currently cannot access the 2.0 Flash model in the tested Vertex locations.
