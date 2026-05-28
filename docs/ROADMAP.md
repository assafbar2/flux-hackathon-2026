# Flux Roadmap

## Immediate (v1.1 — post-hackathon)

- **Live merge request ingestion.** The current build reads GitLab issues live and uses MR data from a pre-loaded fixture for the influence graph. The next step is calling `glab_mr_list` in real time so the ownership map — who reviews what, fastest reviewer turnaround — reflects actual recent activity in the connected org, not demo data.
- **Per-workspace GitLab token passthrough.** HR admins can already enter their own GitLab token in the setup form. Wiring that token through to the live agent calls (currently the deployed service uses a server-side token) would make each Flux workspace fully isolated and org-specific.
- **Persistent workspace storage.** Workspaces are currently held in memory for the hackathon demo. Moving them to Firestore would keep generated onboarding links stable across Cloud Run cold starts and revisions.

## Version 2

- **Daily brief refresh.** Flux currently generates the brief once on first load. A scheduled re-generation (daily or on-demand) would keep the brief current as the team's situation changes — new P1s, someone going on leave, a crunch ending.
- **Multi-repo intelligence.** The current build targets a single GitLab project. Engineering teams typically span 5–20 repos. A v2 influence graph would aggregate reviewer patterns across the full org, surfacing cross-repo ownership signals that a single-project view misses.
- **Slack and Linear integrations.** Notion is the right demo surface for HR-maintained context, but real teams keep tribal knowledge in Slack threads and Linear comments. Connecting those sources would make the brief dramatically richer.
- **Persistent session memory.** Chat context is held in memory and lost on page refresh. Persisting the brief and chat history to a lightweight store (Firestore or Redis) would let new hires return to their Flux session across days.
- **Write actions beyond issue assignment.** The current action is assigning a good-first issue. Natural next actions: posting a "starting work" comment on the issue, creating a draft MR from a template, or scheduling a first coffee with the recommended team contact via calendar API.
