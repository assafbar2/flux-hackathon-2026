from dataclasses import dataclass
from secrets import token_urlsafe


@dataclass(frozen=True)
class Workspace:
    workspace_id: str
    gitlab_token: str
    notion_url: str
    gitlab_username: str | None = None


class WorkspaceStore:
    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}

    def create(
        self,
        *,
        gitlab_token: str,
        notion_url: str,
        gitlab_username: str | None,
    ) -> Workspace:
        workspace_id = token_urlsafe(9)
        workspace = Workspace(
            workspace_id=workspace_id,
            gitlab_token=gitlab_token,
            notion_url=notion_url,
            gitlab_username=gitlab_username,
        )
        self._workspaces[workspace_id] = workspace
        return workspace

    def get(self, workspace_id: str) -> Workspace | None:
        return self._workspaces.get(workspace_id)


store = WorkspaceStore()
