# Submission Checklist

Last updated: May 28, 2026.

## Required By Contest Submission

- [x] Pick partner track: GitLab.
- [x] Hosted project URL exists.
- [x] Public source repository exists.
- [x] Open source license exists.
- [x] App runs on web.
- [x] Uses Google Cloud.
- [x] Uses Gemini.
- [x] Uses Google ADK / Agent Builder style orchestration.
- [x] Uses partner MCP server.
- [x] Moves beyond chat with a tool action.
- [x] Final demo video is uploaded publicly or unlisted.
- [x] Final demo video URL exists: https://youtu.be/oIAdQKI1Kek
- [x] Final Devpost form submitted on May 28, 2026.

## Current Public Links

- App: https://flux-153593352872.us-central1.run.app
- Health: https://flux-153593352872.us-central1.run.app/api/health
- Repo: https://github.com/assafbar2/flux-hackathon-2026
- Demo video: https://youtu.be/oIAdQKI1Kek
- Devpost submission: https://devpost.com/software/flux-veocby

## Devpost Submission

- Hackathon page: https://rapid-agent.devpost.com/
- Submitted project: https://devpost.com/software/flux-veocby
- Copy source: `docs/DEVPOST_SUBMISSION.md`

## Final Video Source

```text
docs/video/barnir-flux-demo.mp4
```

The MP4 is intentionally not committed to GitHub because `docs/video/.gitignore`
excludes generated video files. The public version is hosted on YouTube.

## Pre-Submission Smoke Test

Run:

```bash
backend/.venv/bin/pytest backend/tests -q
cd frontend && npm run build
```

Verify:

- Open the public app.
- Leave setup fields blank.
- Confirm the demo-data note is visible.
- Generate a link.
- Open the onboarding page.
- Ask `Who owns auth?`
- Ask `How do I ship fast?`
- Ask `Assign issue #412 to me`
- Confirm the assignment.
- Show the success message and, if possible, the GitLab issue page.

## Screenshot / Proof Checklist

- [x] README screenshots are committed.
- [x] README screenshots are publicly reachable from GitHub.
- [x] README Mermaid diagram is inline and should render in GitHub.
- [ ] Cloud Run service screenshot.
- [ ] Cloud Logging screenshot for `/api/chat` or `/api/action/confirm`.
- [ ] Optional Agent Platform / Agent Engine screenshot.
