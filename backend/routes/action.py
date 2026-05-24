import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.gitlab_mcp import GitLabMcpClient
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

    if os.getenv("GITLAB_TOKEN") and os.getenv("GITLAB_PROJECT_URL"):
        live_username = os.getenv("GITLAB_USERNAME") if username == "newhire" else username
        username = live_username or username
        try:
            assigned = GitLabMcpClient().assign_demo_issue(
                project=project,
                issue_id=issue_id,
                username=username,
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail="GitLab assignment failed") from exc
        return ActionConfirmResponse(
            success=True,
            message=f"Issue #{issue_id} assigned to {username}.",
            gitlab_url=assigned["gitlab_url"],
        )

    return ActionConfirmResponse(
        success=True,
        message=f"Issue #{issue_id} assigned to {username}.",
        gitlab_url=f"https://gitlab.com/demo/{project}/-/issues/{issue_id}",
    )
