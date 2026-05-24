import asyncio
import os
import re
import urllib.parse
from dataclasses import dataclass
from typing import Any, Protocol

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ISSUE_LINE_RE = re.compile(r"^#(?P<iid>\d+)\t(?P<title>[^\t]+)\t(?P<labels>[^\t]*)\t")


class McpToolClient(Protocol):
    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        ...

    def list_tool_names(self) -> list[str]:
        ...


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
        "assignee": assignees[0]["username"] if assignees else issue.get("assignee"),
        "state": issue.get("state", "opened"),
        "web_url": issue.get("web_url"),
    }


def parse_issue_list(text: str, project_url: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    base_url = project_url.rstrip()
    for line in text.splitlines():
        match = ISSUE_LINE_RE.match(line)
        if not match:
            continue
        labels = [
            label.strip()
            for label in match.group("labels").strip("()").split(",")
            if label.strip()
        ]
        issue = normalize_demo_issue(
            {
                "iid": int(match.group("iid")),
                "title": match.group("title"),
                "labels": labels,
                "state": "opened",
                "assignees": [],
                "web_url": f"{base_url}/-/issues/{match.group('iid')}",
            }
        )
        issues.append(issue)
    return sorted(issues, key=lambda issue: str(issue["id"]))


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError("GitLab MCP synchronous client cannot run inside an active event loop")


@dataclass
class GlabMcpToolClient:
    token: str
    command: str = "glab"

    def list_tool_names(self) -> list[str]:
        return _run_async(self._list_tool_names())

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        return _run_async(self._call_tool(name, arguments))

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["GITLAB_TOKEN"] = self.token
        return env

    async def _list_tool_names(self) -> list[str]:
        params = StdioServerParameters(
            command=self.command,
            args=["mcp", "serve"],
            env=self._env(),
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.name for tool in result.tools]

    async def _call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        params = StdioServerParameters(
            command=self.command,
            args=["mcp", "serve"],
            env=self._env(),
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
                return "\n".join(
                    getattr(block, "text", "")
                    for block in result.content
                    if getattr(block, "text", "")
                )


class GitLabMcpClient:
    """GitLab integration backed by the official `glab mcp serve` server."""

    def __init__(
        self,
        token: str | None = None,
        project_url: str | None = None,
        mcp_client: McpToolClient | None = None,
    ) -> None:
        self.token = token or os.getenv("GITLAB_TOKEN", "")
        self.project_url = (project_url or os.getenv("GITLAB_PROJECT_URL", "")).rstrip("/")
        self.mcp_client = mcp_client or GlabMcpToolClient(self.token)

    @property
    def project_path(self) -> str:
        return self.project_url.removeprefix("https://gitlab.com/").strip("/")

    @property
    def encoded_project_path(self) -> str:
        return urllib.parse.quote(self.project_path, safe="")

    def list_issues(self) -> list[dict[str, Any]]:
        output = self.mcp_client.call_tool(
            "glab_issue_list",
            {
                "flags": {
                    "repo": self.project_path,
                    "output": "text",
                    "per_page": 100,
                },
                "limit": 20000,
            },
        )
        return parse_issue_list(output, self.project_url)

    def fetch_demo_activity(self) -> dict[str, Any]:
        return {
            "issues": self.list_issues(),
            "merge_requests": [],
            "mcp_tools": self.mcp_client.list_tool_names(),
        }

    def find_issue_by_demo_id(self, project: str, issue_id: str) -> dict[str, Any]:
        for issue in self.list_issues():
            if issue["project"] == project and str(issue["id"]) == str(issue_id):
                return issue
        raise ValueError(f"No GitLab issue found for {project}/#{issue_id}")

    def assign_demo_issue(self, *, project: str, issue_id: str, username: str) -> dict[str, Any]:
        issue = self.find_issue_by_demo_id(project, issue_id)
        issue_url = issue["web_url"] or f"{self.project_url}/-/issues/{issue['iid']}"
        self.mcp_client.call_tool(
            "glab_issue_update",
            {
                "args": [issue_url],
                "flags": {"assignee": [username]},
                "limit": 20000,
            },
        )
        return {
            "iid": issue["iid"],
            "gitlab_url": issue_url,
            "mcp_tool": "glab_issue_update",
        }
