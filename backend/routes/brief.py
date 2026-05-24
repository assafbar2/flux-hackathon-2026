from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.agent_builder import build_flux_brief
from services.store import store


router = APIRouter()


class BriefSection(BaseModel):
    title: str
    body: str
    sources: list[str]


class BriefResponse(BaseModel):
    workspace_id: str
    brief: dict[str, BriefSection]


@router.get("/brief/{workspace_id}", response_model=BriefResponse)
def get_brief(workspace_id: str) -> BriefResponse:
    if store.get(workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return BriefResponse(workspace_id=workspace_id, brief=build_flux_brief())
