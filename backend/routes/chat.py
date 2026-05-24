from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.demo_intelligence import answer_demo_question
from services.store import store


router = APIRouter()


class ChatRequest(BaseModel):
    workspace_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    action: dict | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    workspace = store.get(payload.workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return ChatResponse(**answer_demo_question(payload.message, workspace.gitlab_username))
