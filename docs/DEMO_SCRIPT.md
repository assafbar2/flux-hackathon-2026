# Flux Demo Script

Final hosted video: https://youtu.be/oIAdQKI1Kek

Final runtime: 2:28. The first 33 seconds are intentionally held on the Flux setup page so the personal intro can be read cleanly before the product walkthrough starts.

## Voiceover

### 0:00-0:33 - Personal Intro

Hi, I'm Assaf Barnir. I'm an ex-engineer who moved into customer-facing roles, and the recent advances in AI brought me back to building.

Flux comes from a pain I've seen from both sides: as a hiring manager and as someone being hired myself. Onboarding looks documented, but the truth of how a team works is usually scattered across tools and people.

### 0:33-0:41 - Flux Framing

Flux is built for the reality that companies are always in flux, and new hires are too. The org chart is stale the moment it's printed. Flux reads what is actually moving.

### 0:41-0:48 - GitLab Source

Here are the raw ingredients. GitLab gives real issues, ownership signals, review activity, and the work a new hire can actually pick up.

### 0:48-0:59 - Notion Source

Notion gives the human context: who owns what, who is unavailable, what not to touch, and the unwritten rules that never make it into formal onboarding.

### 0:59-1:10 - Cloud Run Proof

And this runs live on Google Cloud Run. The service is deployed, observable, and serving requests from the public Flux app.

### 1:10-1:23 - Generate Link

Now the new hire opens Flux. They don't need to configure anything for the demo. Flux uses the deployed GitLab and Notion data to generate a live onboarding brief.

### 1:23-1:38 - Brief

The brief is not a static checklist. It says what is happening now, who actually owns each area, what is safe to work on in week one, and what political landmines to avoid.

### 1:38-1:55 - Grounded Q&A

Then the new hire can ask practical questions: who owns auth, how to ship fast, and what not to say in standup. Answers are grounded in GitLab activity and the team guide.

### 1:55-2:17 - Confirmed GitLab Action

The key move beyond chat is action. Flux proposes assigning billing issue 412, waits for confirmation, then writes back to GitLab through the MCP path.

So Flux turns onboarding from a frozen PDF into a living, grounded, action-taking agent for week one.

### 2:17-2:28 - Visual Tail

No additional voiceover. The video leaves the confirmed assignment and final app state on screen.

## What The Video Shows

- The public Flux app at `https://flux-153593352872.us-central1.run.app`.
- GitLab as the partner system of record for issues, ownership signals, and confirmed issue assignment.
- Notion as the human team guide for availability, norms, and unwritten rules.
- Cloud Run logs as deployment and observability proof.
- A blank-field setup flow using deployed demo data, so judges can click through without entering credentials.
- The new-hire brief, grounded Q&A, and confirmed `Assign issue #412 to me` flow.

## Backup Demo Lines

If the GitLab issue is already assigned:

> The live action path is connected. This issue is already assigned from a previous run, which is what we expect after a successful demo.

If asked about Agent Builder:

> The deployed build uses the code-first Google Agent Builder / Agent Platform path: Google ADK LlmAgent plus Runner, Gemini as the model, and GitLab exposed through the official GitLab CLI MCP server. The product runtime is Cloud Run because the judges need a complete web app with onboarding links and action confirmation.

If asked what to show in Google Cloud:

> Show the Cloud Run service, the live health check, and Cloud Logging for `/api/brief`, `/api/chat`, or `/api/action/confirm`. The runtime environment shows `FLUX_AGENT_MODE=live`, Gemini model settings, and Secret Manager references for GitLab and Notion tokens without exposing secret values.
