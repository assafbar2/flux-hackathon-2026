import os

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.store import store


router = APIRouter()


class SetupRequest(BaseModel):
    gitlab_token: str = Field(min_length=1)
    notion_url: str = Field(min_length=1)
    gitlab_username: str | None = None


class SetupResponse(BaseModel):
    workspace_id: str
    hire_link: str


@router.post("/setup", response_model=SetupResponse)
def setup_workspace(payload: SetupRequest) -> SetupResponse:
    workspace = store.create(
        gitlab_token=payload.gitlab_token,
        notion_url=payload.notion_url,
        gitlab_username=payload.gitlab_username,
    )
    base_url = os.getenv("FLUX_BASE_URL", "http://localhost:5173").rstrip("/")
    return SetupResponse(
        workspace_id=workspace.workspace_id,
        hire_link=f"{base_url}/onboard/{workspace.workspace_id}",
    )
