from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.store import store


router = APIRouter()


class ChatRequest(BaseModel):
    workspace_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    action: dict | None = None


def demo_answer(message: str, gitlab_username: str | None) -> ChatResponse:
    normalized = message.lower()
    if "assign" in normalized and "412" in normalized:
        return ChatResponse(
            answer="I can assign billing issue #412 to you. Confirm first and I will call GitLab MCP to make the assignment.",
            sources=["GitLab activity"],
            action={
                "type": "assign_issue",
                "issue_id": "412",
                "project": "billing",
                "username": gitlab_username or "newhire",
            },
        )

    if "auth" in normalized or "owns" in normalized:
        return ChatResponse(
            answer="Marcus actually owns the auth system. Based on GitLab activity over the last 90 days, he reviewed 71% of auth PRs; the team guide also names him as the person to contact for auth questions.",
            sources=["GitLab activity", "Team guide"],
        )

    return ChatResponse(
        answer="For week 1, start in billing or notifications. The team guide marks both as safe zones, and GitLab shows billing issue #412 and notifications issue #89 as good first tasks.",
        sources=["GitLab activity", "Team guide"],
    )


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    workspace = store.get(payload.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return demo_answer(payload.message, workspace.gitlab_username)
