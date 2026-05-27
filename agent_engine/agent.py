import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


def _gitlab_toolset() -> McpToolset:
    env = os.environ.copy()
    if os.getenv("GITLAB_TOKEN"):
        env["GITLAB_TOKEN"] = os.environ["GITLAB_TOKEN"]
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=os.getenv("GLAB_COMMAND", "glab"),
                args=["mcp", "serve"],
                env=env,
            ),
            timeout=10,
        ),
        tool_filter=[
            "glab_issue_list",
            "glab_issue_view",
            "glab_issue_update",
            "glab_mr_list",
            "glab_repo_list",
            "glab_api",
        ],
    )


root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    name="flux_onboarding_agent",
    instruction=(
        "You are Flux, an onboarding intelligence agent. Help a new engineer understand "
        "the living state of a GitLab-based team. Use GitLab MCP tools for GitLab facts, "
        "cite sources, and require explicit confirmation before any write action."
    ),
    tools=[_gitlab_toolset()],
)
