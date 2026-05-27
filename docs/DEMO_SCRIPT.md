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

> Hi, I'm Assaf. I built Flux for the Google Cloud Rapid Agent Hackathon because onboarding is still treated like a document problem, when it is really a live-context problem.
>
> I started as an engineer, moved into customer-facing roles, and the latest advances in AI brought me back to building. That mix is why this problem matters to me: onboarding fails at the exact place where product, people, and real work meet.
>
> Every month, millions of people start new jobs. In engineering, week one is usually a PDF, a stale wiki, and a manager saying "just ask around." But a new hire doesn't need the official org chart. They need to know who actually reviews auth, what is on fire this week, which work is safe to touch, and what unwritten rules could trip them up.
>
> That gap costs real money. Engineers often take 60 to 90 days to become productive, and every slow ramp burns salary, manager time, and team momentum.
>
> Flux fixes this with a live agent that reads the actual work in GitLab, combines it with the team's Notion guide, and gives the new hire the real org, not the drawn one.

Optional visual:

- Show a stale onboarding PDF or the Flux landing page while speaking.

### 0:40-0:55 — HR Setup

Action:

1. Show the Flux setup page.
2. Leave the fields blank for demo mode.
3. Click `Generate link`.
4. Open the generated onboarding link.

Say:

> HR only needs a GitLab token and a Notion team guide URL. For this demo, the production service already has secure server-side configuration, so I can generate a new-hire link without putting secrets in the browser. Behind this page, Flux runs on Cloud Run. The backend creates a Google ADK LlmAgent, runs it through the ADK Runner, uses Gemini as the reasoning model, and registers GitLab MCP tools through glab mcp serve.

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

> Flux moves beyond chat. It proposes a concrete first task, asks for confirmation, and then writes back to GitLab through the GitLab MCP server. In the code path, the confirmed action calls glab_issue_update, so the agent is not just answering — it is taking a controlled action in a live partner system.

### 2:50-3:00 — Close

Say:

> Every engineer deserves this on day one: not a PDF, not a stale org chart, but the real team context and a first task already assigned. And every company that wants to be AI-first should show it in the first experience a new hire has.

## Backup Lines

If the GitLab write is already assigned:

> The live action path is connected. This issue is already assigned from a previous run, which is what we expect after a successful demo.

If Notion is slow:

> Flux has deterministic fallback data for demo reliability, but the deployed service is configured to read the live Notion team guide when available.

If asked about Agent Builder:

> The deployed build uses the code-first Google Agent Builder / Agent Platform path: Google ADK LlmAgent plus Runner, Gemini as the model, and GitLab exposed through the official GitLab CLI MCP server. The product runtime is Cloud Run because the judges need a complete web app with onboarding links and action confirmation. I also have an Agent Builder proof note and a companion Agent Engine artifact in the repo if a console screenshot is needed.

If asked what to show in Google Cloud:

> Show the Cloud Run service, the live health check, and Cloud Logging for /api/brief, /api/chat, or /api/action/confirm. The runtime environment shows FLUX_AGENT_MODE=live, Gemini model settings, and Secret Manager references for GitLab and Notion tokens without exposing secret values.
