# Agent Builder / Agent Platform Proof

Last updated: May 27, 2026.

## Requirement Reading

The Devpost requirement says Flux must be a functional agent powered by Gemini and Google Cloud Agent Builder, with a partner MCP server. It does not explicitly require a console-created Agent Builder artifact or screenshot.

Flux satisfies the code-first Agent Builder path by using Google ADK on Cloud Run:

- `backend/services/agent_builder.py` creates a Google ADK `LlmAgent`.
- The agent runs through a Google ADK `Runner`.
- Gemini is the reasoning model.
- GitLab MCP is registered as an ADK `McpToolset`.
- Cloud Run hosts the public web app.

Google's Agent Platform docs describe ADK as a supported framework for building agents and Agent Platform Runtime as a managed destination for ADK agents. The current production path is Cloud Run because the hackathon also requires a hosted web project that judges can click.

## Current Runtime Evidence

Public health check:

```text
GET https://flux-153593352872.us-central1.run.app/api/health
{"status":"ok","mode":"live","version":"1.0.0"}
```

Cloud Run service:

```text
service: flux
region: us-central1
project: direct-subject-497307-p8
latest verified revision: flux-00012-n47
```

Agent code evidence:

```text
backend/services/agent_builder.py
- LlmAgent(...)
- Runner(...)
- McpToolset(...)
- StdioServerParameters(command="glab", args=["mcp", "serve"])
```

GitLab MCP write evidence:

```text
backend/services/gitlab_mcp.py
- glab_issue_list
- glab_issue_update
```

## Console Proof To Capture Before Submission

Capture these screenshots for the Devpost video or README if time allows:

1. Cloud Run service details for `flux`, showing the public URL and latest revision.
2. Cloud Run revision environment variables showing `FLUX_AGENT_MODE=live`, `GOOGLE_GENAI_USE_VERTEXAI=True`, and Gemini model settings. Do not show secret values.
3. Cloud Logging filtered to `flux`, showing requests to `/api/brief`, `/api/chat`, or `/api/action/confirm`.
4. Secret Manager showing secret names only: `flux-gitlab-token` and `flux-notion-token`.
5. Optional Agent Platform / Agent Engine page if a companion Agent Engine deployment is created.

## Optional Agent Engine Companion Artifact

If judges appear to expect an Agent Builder console artifact, create a companion Vertex AI Agent Engine deployment from the same ADK structure. This is not the primary product runtime; it is a proof artifact showing the agent can be represented as an Agent Platform Runtime agent.

Suggested naming:

```text
display name: flux-onboarding-agent
framework: google-adk
description: Flux onboarding intelligence agent using Gemini and GitLab MCP.
```

The production demo should still use the Cloud Run URL because it contains the full React onboarding experience and action-confirmation UI.
