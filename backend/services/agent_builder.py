import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any

from google.api_core.exceptions import NotFound, ResourceExhausted, ServiceUnavailable
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from google.genai.errors import ClientError, ServerError
from mcp import StdioServerParameters

from services.demo_intelligence import (
    answer_demo_question,
    build_demo_brief,
    load_team_guide_text,
)
from services.gitlab_mcp import GitLabMcpClient
from services.influence_graph import build_influence_graph
from services.notion_parser import parse_team_guide


BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "brief": {
            "type": "object",
            "properties": {
                "now": {"$ref": "#/$defs/section"},
                "people": {"$ref": "#/$defs/section"},
                "moves": {"$ref": "#/$defs/section"},
                "landmines": {"$ref": "#/$defs/section"},
            },
            "required": ["now", "people", "moves", "landmines"],
        }
    },
    "required": ["brief"],
    "$defs": {
        "section": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "sources": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "body", "sources"],
        }
    },
}

CHAT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
        "action": {
            "anyOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "issue_id": {"type": "string"},
                        "project": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["type", "issue_id", "project", "username"],
                },
            ]
        },
    },
    "required": ["answer", "sources", "action"],
}

VERTEX_RETRY_LOCATIONS = ("us-central1", "us-east4", "us-west1", "europe-west4")
RETRIABLE_VERTEX_ERRORS = (NotFound, ServiceUnavailable, ResourceExhausted)
RETRIABLE_GENAI_STATUS_CODES = {404, 429, 503}


def live_mode_enabled() -> bool:
    return os.getenv("FLUX_AGENT_MODE", "demo").lower() == "live"


def load_live_context() -> dict[str, Any]:
    guide_text, guide_source = load_team_guide_text()
    gitlab_activity = GitLabMcpClient().fetch_demo_activity()
    return {
        "team_guide_source": guide_source,
        "team_guide": parse_team_guide(guide_text),
        "gitlab_activity": gitlab_activity,
        "influence_graph": build_influence_graph(gitlab_activity),
    }


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("ADK response did not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def _vertex_locations() -> list[str]:
    configured = os.getenv("GOOGLE_CLOUD_LOCATION", "").strip()
    locations = [configured] if configured else []
    locations.extend(VERTEX_RETRY_LOCATIONS)
    return list(dict.fromkeys(location for location in locations if location))


def _is_retriable_vertex_error(exc: Exception) -> bool:
    if isinstance(exc, RETRIABLE_VERTEX_ERRORS):
        return True
    if isinstance(exc, (ClientError, ServerError)):
        return getattr(exc, "code", None) in RETRIABLE_GENAI_STATUS_CODES
    return False


async def _try_vertex_locations(
    model: str,
    agent_factory_fn: Callable[[str], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    last_error: Exception | None = None
    for location in _vertex_locations():
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        try:
            return await agent_factory_fn(model)
        except Exception as exc:
            if not _is_retriable_vertex_error(exc):
                raise
            last_error = exc
    if last_error:
        raise last_error
    return await agent_factory_fn(model)


class AdkGeminiRunner:
    """Google ADK runner using Gemini and the GitLab MCP toolset."""

    def __init__(self, model: str | None = None, fallback_model: str | None = None) -> None:
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.fallback_model = fallback_model or os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

    def generate_json(self, *, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return asyncio.run(self._generate_json(task=task, payload=payload, model=self.model))
        except RETRIABLE_VERTEX_ERRORS:
            if self.fallback_model and self.fallback_model != self.model:
                return asyncio.run(
                    self._generate_json(task=task, payload=payload, model=self.fallback_model)
                )
            raise
        except Exception:
            if self.fallback_model and self.fallback_model != self.model:
                return asyncio.run(
                    self._generate_json(task=task, payload=payload, model=self.fallback_model)
                )
            raise

    async def _generate_json(self, *, task: str, payload: dict[str, Any], model: str) -> dict[str, Any]:
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true":
            return await _try_vertex_locations(
                model,
                lambda candidate_model: self._run_adk_agent(
                    task=task,
                    payload=payload,
                    model=candidate_model,
                ),
            )
        return await self._run_adk_agent(task=task, payload=payload, model=model)

    async def _run_adk_agent(
        self,
        *,
        task: str,
        payload: dict[str, Any],
        model: str,
    ) -> dict[str, Any]:
        toolset = self._gitlab_toolset()
        agent = LlmAgent(
            model=model,
            name="flux_agent",
            instruction=self._instruction(task),
            tools=[toolset],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="flux_agent",
            user_id="flux_user",
        )
        runner = Runner(
            app_name="flux_agent",
            agent=agent,
            session_service=session_service,
            artifact_service=InMemoryArtifactService(),
        )
        message = types.Content(
            role="user",
            parts=[types.Part(text=json.dumps(payload, ensure_ascii=False))],
        )
        chunks: list[str] = []
        try:
            async for event in runner.run_async(
                user_id="flux_user",
                session_id=session.id,
                new_message=message,
            ):
                content = getattr(event, "content", None)
                if not content:
                    continue
                for part in content.parts or []:
                    if getattr(part, "text", None):
                        chunks.append(part.text)
        finally:
            await toolset.close()
        return _extract_json("\n".join(chunks))

    def _gitlab_toolset(self) -> McpToolset:
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

    def _instruction(self, task: str) -> str:
        if task == "brief":
            return (
                "You are Flux, an onboarding intelligence agent. Use the supplied GitLab MCP "
                "activity, Notion team guide, and influence graph. Return only JSON matching "
                "this shape: {\"brief\":{\"now\":section,\"people\":section,\"moves\":section,"
                "\"landmines\":section}} where section has title, body, sources. Sources must "
                "name GitLab MCP or Notion. Do not invent people or issues."
            )
        return (
            "You are Flux, an onboarding intelligence agent. Answer from the supplied context. "
            "Return only JSON with answer, sources, and action. Sources must include GitLab MCP "
            "for GitLab-derived facts and Notion for team-guide-derived facts. If the user asks to assign issue "
            "#412, return an action {type:'assign_issue', issue_id:'412', project:'billing', "
            "username:<provided username>} and explain that confirmation is required before "
            "the GitLab MCP write."
        )


def build_flux_brief() -> dict[str, dict[str, Any]]:
    if not live_mode_enabled():
        return build_demo_brief()
    try:
        generated = AdkGeminiRunner().generate_json(task="brief", payload=load_live_context())
        return generated["brief"]
    except Exception:
        return build_demo_brief()


def answer_flux_question(message: str, gitlab_username: str | None) -> dict[str, Any]:
    if not live_mode_enabled():
        return answer_demo_question(message, gitlab_username)
    try:
        generated = AdkGeminiRunner().generate_json(
            task="chat",
            payload={
                "message": message,
                "gitlab_username": gitlab_username or os.getenv("GITLAB_USERNAME", "newhire"),
                "context": load_live_context(),
            },
        )
        generated.setdefault("action", None)
        return generated
    except Exception:
        return answer_demo_question(message, gitlab_username)
