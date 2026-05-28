# Submission Form Draft

Use this as the copy source for the final contest submission form.

Submitted on May 28, 2026: https://devpost.com/software/flux-veocby

## Project Name

Flux

## Tagline

The org as it runs, not as it is drawn.

## Track

GitLab

## Hosted Project URL

https://flux-153593352872.us-central1.run.app

## Repository URL

https://github.com/assafbar2/flux-hackathon-2026

## Demo Video URL

https://youtu.be/oIAdQKI1Kek

Upload source file: `docs/video/barnir-flux-demo.mp4`

## Short Description

Flux gives every new hire the real team map on day one: what is moving, who owns what, what to avoid, and the first GitLab issue they can safely take. It uses Google ADK, Gemini, GitLab MCP, Notion, and Cloud Run to turn live work signals into grounded onboarding guidance and confirmed GitLab actions.

## What It Does

Flux creates a new-hire link from a setup page. The new hire opens the link and sees a four-part brief:

- Right Now: current fires, blockers, and sensitive areas.
- Your People Map: who actually owns systems based on GitLab review and issue activity.
- Week 1 Moves: safe first issues and modules.
- Landmines: unwritten rules from the team guide.

The new hire can ask follow-up questions with source attribution. If they ask to take issue `#412`, Flux proposes the assignment, asks for confirmation, and calls GitLab MCP to write the assignment back to GitLab.

## How We Built It

- Frontend: React, TypeScript, Vite.
- Backend: FastAPI.
- Hosting: Google Cloud Run.
- Agent orchestration: Google ADK `LlmAgent` and `Runner`, positioned as the code-first Agent Builder / Agent Platform path.
- Model: Gemini 2.0 Flash primary with Gemini 2.5 Flash fallback for Vertex availability.
- Partner integration: official GitLab CLI MCP server through `glab mcp serve`.
- Team guide: Notion API with deterministic fallback data.
- Secrets: Google Secret Manager.

## Google Cloud And Partner Usage

Flux uses Google Cloud for the deployed runtime, secret management, and Gemini-powered agent orchestration. The production service runs on Cloud Run in live mode. The backend uses Google ADK to create the agent, route Gemini calls, and register GitLab MCP tools.

GitLab is the partner track. Flux uses GitLab MCP for both reads and writes:

- `glab_issue_list` reads issue activity for the brief and first-task recommendations.
- `glab_issue_update` assigns an issue after the new hire confirms.

## What We Learned

The biggest onboarding gap is not lack of documentation. It is lack of living ground truth. GitLab knows what work is actually moving; Notion knows the human context. The agent becomes valuable when it combines both and then acts safely with a human confirmation step.

We also learned that hackathon demos need reliability. Flux keeps deterministic fallback data so judges can evaluate the product even if an external API is slow, while the deployed live mode still uses Cloud Run, Gemini, ADK, Notion, and GitLab MCP.

## Judging Criteria Notes

- Technological implementation: live Cloud Run app, Gemini/ADK agent, GitLab MCP read/write, Secret Manager, tested backend.
- Design: single-link new-hire flow, source attribution, explicit action confirmation, visible demo-data mode.
- Potential impact: every fast-growing company has stale onboarding and expensive ramp time.
- Quality of idea: Flux maps the living team, not the frozen org chart.
