import os
import re
import urllib.parse
from typing import Any

import httpx


def normalize_demo_issue(issue: dict[str, Any]) -> dict[str, Any]:
    marker = re.search(r"\[([^/\]]+)/#?([^\]]+)\]", issue.get("title", ""))
    project = marker.group(1) if marker else "project"
    display_id = marker.group(2) if marker else str(issue.get("iid", ""))
    assignees = issue.get("assignees") or []
    return {
        "id": display_id,
        "iid": issue.get("iid"),
        "project": project,
        "title": issue.get("title", ""),
        "labels": issue.get("labels", []),
        "assignee": assignees[0]["username"] if assignees else None,
        "state": issue.get("state", "opened"),
        "web_url": issue.get("web_url"),
    }


class GitLabMcpClient:
    """Thin GitLab tool adapter.

    The public methods match the MCP operations Flux needs, while this first
    implementation talks to GitLab's HTTP API until the Agent Builder MCP
    runtime is wired in.
    """

    def __init__(
        self,
        token: str | None = None,
        project_url: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.token = token or os.getenv("GITLAB_TOKEN", "")
        self.project_url = (project_url or os.getenv("GITLAB_PROJECT_URL", "")).rstrip("/")
        self.http = http_client or httpx.Client(timeout=20)

    @property
    def project_path(self) -> str:
        return self.project_url.removeprefix("https://gitlab.com/").strip("/")

    @property
    def encoded_project_path(self) -> str:
        return urllib.parse.quote(self.project_path, safe="")

    @property
    def base_url(self) -> str:
        return f"https://gitlab.com/api/v4/projects/{self.encoded_project_path}"

    def _headers(self) -> dict[str, str]:
        return {"PRIVATE-TOKEN": self.token}

    def list_issues(self) -> list[dict[str, Any]]:
        response = self.http.get(
            f"{self.base_url}/issues",
            headers=self._headers(),
            params={"per_page": 100},
        )
        response.raise_for_status()
        return response.json()

    def fetch_demo_activity(self) -> dict[str, Any]:
        return {
            "issues": [normalize_demo_issue(issue) for issue in self.list_issues()],
        }

    def find_issue_by_demo_id(self, project: str, issue_id: str) -> dict[str, Any]:
        marker = f"[{project}/#{issue_id}]"
        for issue in self.list_issues():
            if marker in issue.get("title", ""):
                return issue
        raise ValueError(f"No GitLab issue found for {project}/#{issue_id}")

    def find_user_id(self, username: str) -> int:
        response = self.http.get(
            "https://gitlab.com/api/v4/users",
            headers=self._headers(),
            params={"username": username},
        )
        response.raise_for_status()
        users = response.json()
        if not users:
            raise ValueError(f"No GitLab user found for {username}")
        return int(users[0]["id"])

    def assign_issue(self, issue_iid: int, username: str) -> dict[str, Any]:
        user_id = self.find_user_id(username)
        response = self.http.put(
            f"{self.base_url}/issues/{issue_iid}",
            headers=self._headers(),
            data={"assignee_ids": [user_id]},
        )
        response.raise_for_status()
        return response.json()

    def assign_demo_issue(self, *, project: str, issue_id: str, username: str) -> dict[str, Any]:
        issue = self.find_issue_by_demo_id(project, issue_id)
        assigned = self.assign_issue(int(issue["iid"]), username)
        return {
            "iid": assigned["iid"],
            "gitlab_url": assigned["web_url"],
        }
