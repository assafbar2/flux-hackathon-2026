from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.store import store


router = APIRouter()


class ActionConfirmRequest(BaseModel):
    workspace_id: str
    action: dict


class ActionConfirmResponse(BaseModel):
    success: bool
    message: str
    gitlab_url: str


@router.post("/action/confirm", response_model=ActionConfirmResponse)
def confirm_action(payload: ActionConfirmRequest) -> ActionConfirmResponse:
    if store.get(payload.workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    action = payload.action
    if action.get("type") != "assign_issue":
        raise HTTPException(status_code=400, detail="Unsupported action")

    issue_id = action.get("issue_id")
    project = action.get("project")
    username = action.get("username")
    if not issue_id or not project or not username:
        raise HTTPException(status_code=400, detail="Incomplete assignment action")

    return ActionConfirmResponse(
        success=True,
        message=f"Issue #{issue_id} assigned to {username}.",
        gitlab_url=f"https://gitlab.com/demo/{project}/-/issues/{issue_id}",
    )
