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

## Current Build Mode

Flux should support `FLUX_AGENT_MODE=demo` before live integrations are wired. Demo mode uses deterministic fixtures so the hackathon demo can stay reliable while GitLab MCP, Notion, and Agent Builder access are being configured.

## Submission Checklist

- Hosted Cloud Run URL
- Public GitHub repo
- MIT license
- Setup instructions a judge can follow
- Demo video under 3 minutes
- GitLab partner track selected
