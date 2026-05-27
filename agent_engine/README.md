# Flux Agent Engine Companion Artifact

This folder is a minimal companion artifact for proving the same Flux ADK agent shape can be represented for Vertex AI Agent Engine / Google Agent Platform.

The production demo remains the Cloud Run web app because it includes the React onboarding flow and explicit action-confirmation UI.

Use this only if the final submission needs an Agent Platform console screenshot in addition to the Cloud Run product demo.

## Why This Exists

The live product already uses:

- Google ADK `LlmAgent`
- Google ADK `Runner`
- Gemini
- GitLab MCP tools
- Cloud Run

This folder gives us a small, reviewable source artifact for an Agent Engine companion deployment without moving the whole web app.

## Files

- `agent.py`: defines `root_agent`.
- `requirements.txt`: minimal runtime dependencies.
- `deploy_agent_engine.py`: deployment scaffold with placeholders.

## Before Deploying

Confirm the exact current Agent Engine deploy API in the Google Cloud docs, then replace the placeholder values in `deploy_agent_engine.py`.

Expected values:

```text
PROJECT_ID=direct-subject-497307-p8
LOCATION=us-central1 or us-east4
DISPLAY_NAME=flux-onboarding-agent
AGENT_FRAMEWORK=google-adk
```

Do not deploy with secret values printed to logs.
