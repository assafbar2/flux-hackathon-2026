## The Team (Real Talk)

### Marcus Chen — Senior Engineer
- Real ownership: Auth system, payments integration (reviews 70%+ of PRs in these areas)
- Availability: Offline Fridays after 4pm (school pickup). Back on Slack by 8pm.
- Bandwidth: Available — good time to connect
- Best way: Slack DM first, then schedule a 30min pairing session

### Sarah Kim — Staff Engineer / Architect
- Real ownership: System architecture, data model decisions
- Availability: On parental leave until June 15, 2026
- Bandwidth: Unavailable until June 15
- Best way: Don't ping her until she's back. Talk to Dev instead.

### Priya Patel — Engineering Lead (nominal)
- Real ownership: Team process, roadmap, 1:1s
- Availability: Normal hours, but 80% focused on enterprise migration until Q3
- Bandwidth: Limited for new hire unblocking — go to Marcus
- Best way: Thursday 1:1 is the right venue for anything strategic

### Dev Sharma — Senior Engineer
- Real ownership: Infrastructure, CI/CD pipeline, deploy process
- Availability: Standard hours
- Bandwidth: Available
- Best way: #eng-infra channel for infra questions, DM for urgent

## Right Now (updated May 2026)

- **Active crunch:** Project Atlas (frontend rewrite) — ends May 30. Don't book frontend eng time until June.
- **Live P1:** SSO migration — Marcus owns it, blocked on Okta vendor response. ETA unknown. Don't touch /auth module.
- **Safe zones for new hires:** billing module, notifications service, docs improvements
- **Good first issues:** billing/#412 (no assignee, clear spec), notifications/#89 (small feature, well-scoped)
- **Politically sensitive:** The v1 to v2 API migration has been contentious. Don't ask why we didn't do it differently.

## Unwritten Rules

- Don't ask "why didn't you use GraphQL?" in public — there's a 2-year history, you don't want to open it
- Friday deploys require explicit +1 from Marcus OR Dev. No exceptions, even hotfixes.
- #eng-general is read by the CEO and investors. Real technical conversations happen in #eng-real.
- Tuesday standup is performative and goes on Loom. The actual team sync is Thursday's eng retro.
- PR template is mandatory. Skip it and it gets returned without review, no exceptions.
- We don't do code ownership files — but Marcus/auth and Dev/infra are the de facto owners.

## How to Ship Here

- **Fastest reviewer:** Marcus — average 2hr turnaround on auth/payments PRs. Tag him.
- **Second fastest:** Dev — average 4hr for infra/backend PRs.
- **PR template:** Use it. Check all the boxes. If a box doesn't apply, strike it out don't delete it.
- **Friday rule:** No deploys on Fridays without +1 from Marcus or Dev. Even small ones.
- **Deploy process:** merge to main → CI runs → auto-deploys to staging → manual promote to prod (Dev owns this)
- **Definition of done:** PR merged + staging verified + ticket closed + #eng-shipping message posted
