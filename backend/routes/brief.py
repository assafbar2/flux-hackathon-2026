from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.store import store


router = APIRouter()


class BriefSection(BaseModel):
    title: str
    body: str
    sources: list[str]


class BriefResponse(BaseModel):
    workspace_id: str
    brief: dict[str, BriefSection]


def demo_brief() -> dict[str, BriefSection]:
    return {
        "now": BriefSection(
            title="Right Now",
            body="The SSO migration is a live P1. Marcus owns it and is blocked on an Okta vendor response. Do not touch the auth module this week.",
            sources=["GitLab activity", "Team guide"],
        ),
        "people": BriefSection(
            title="Your People Map",
            body="Marcus is the de facto auth owner: he reviewed 71% of auth PRs in the last 90 days. Dev owns infra and CI/CD. Sarah is on leave until June 15, 2026.",
            sources=["GitLab activity", "Team guide"],
        ),
        "moves": BriefSection(
            title="Week 1 Moves",
            body="Start in billing or notifications. Billing issue #412 is unassigned with a clear spec, and notifications issue #89 is small and well-scoped.",
            sources=["GitLab activity", "Team guide"],
        ),
        "landmines": BriefSection(
            title="Landmines",
            body="Do not ask why the team did not use GraphQL in public. Friday deploys require explicit +1 from Marcus or Dev. Tuesday standup is performative.",
            sources=["Team guide"],
        ),
    }


@router.get("/brief/{workspace_id}", response_model=BriefResponse)
def get_brief(workspace_id: str) -> BriefResponse:
    if store.get(workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return BriefResponse(workspace_id=workspace_id, brief=demo_brief())
