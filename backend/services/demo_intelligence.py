import json
import os
from pathlib import Path
from typing import Any

from services.influence_graph import build_influence_graph
from services.notion import NotionClient
from services.notion_parser import parse_team_guide


DATA_DIR = Path(__file__).resolve().parents[1] / "demo_data"


def load_team_guide_text() -> tuple[str, str]:
    token = os.getenv("NOTION_TOKEN", "")
    page_url = os.getenv("NOTION_PAGE_URL", "")
    if token and page_url:
        try:
            live_text = NotionClient(token).fetch_page_markdown(page_url)
        except Exception:
            live_text = ""
        if live_text.strip():
            return live_text, "live_notion"

    return (DATA_DIR / "notion_page.md").read_text(encoding="utf-8"), "fixture"


def load_demo_context() -> dict[str, Any]:
    notion_text, notion_source = load_team_guide_text()
    gitlab_activity = json.loads((DATA_DIR / "gitlab_activity.json").read_text(encoding="utf-8"))
    return {
        "team_guide": parse_team_guide(notion_text),
        "team_guide_source": notion_source,
        "activity": gitlab_activity,
        "graph": build_influence_graph(gitlab_activity),
    }


def build_demo_brief() -> dict[str, dict[str, Any]]:
    context = load_demo_context()
    auth_owner = context["graph"]["owners"]["auth"]
    issue = context["graph"]["good_first_issues"][0]
    fire = context["graph"]["active_fires"][0]

    return {
        "now": {
            "title": "Right Now",
            "body": f"{fire['title']}. Marcus owns it and is blocked on an Okta vendor response. Do not touch the auth module this week.",
            "sources": ["GitLab activity", "Team guide"],
        },
        "people": {
            "title": "Your People Map",
            "body": f"{auth_owner['owner']} is the de facto auth owner: he reviewed {int(auth_owner['review_share'] * 100)}% of auth PRs in the last 90 days. Dev owns infra and CI/CD. Sarah is on leave until June 15, 2026.",
            "sources": ["GitLab activity", "Team guide"],
        },
        "moves": {
            "title": "Week 1 Moves",
            "body": f"Start in billing or notifications. Billing issue #{issue['id']} is unassigned with a clear spec, and notifications issue #89 is small and well-scoped.",
            "sources": ["GitLab activity", "Team guide"],
        },
        "landmines": {
            "title": "Landmines",
            "body": "Do not ask why the team did not use GraphQL in public. Friday deploys require explicit +1 from Marcus or Dev. Tuesday standup is performative.",
            "sources": ["Team guide"],
        },
    }


def answer_demo_question(message: str, gitlab_username: str | None) -> dict[str, Any]:
    context = load_demo_context()
    normalized = message.lower()
    username = gitlab_username or "newhire"

    if "assign" in normalized and "412" in normalized:
        return {
            "answer": "I can assign billing issue #412 to you. Confirm first and I will call GitLab MCP to make the assignment.",
            "sources": ["GitLab activity"],
            "action": {
                "type": "assign_issue",
                "issue_id": "412",
                "project": "billing",
                "username": username,
            },
        }

    if "auth" in normalized or "owns" in normalized:
        owner = context["graph"]["owners"]["auth"]
        return {
            "answer": f"Marcus actually owns the auth system. Based on GitLab activity over the last 90 days, he reviewed {int(owner['review_share'] * 100)}% of auth PRs; the team guide also names him as the person to contact for auth questions.",
            "sources": ["GitLab activity", "Team guide"],
            "action": None,
        }

    if "avoid" in normalized or "ping" in normalized:
        return {
            "answer": "Avoid pinging Sarah until June 15, 2026 because the team guide says she is on parental leave. Priya is also limited because she is 80% focused on the enterprise migration; go to Marcus for new-hire unblocking.",
            "sources": ["Team guide", "GitLab activity"],
            "action": None,
        }

    if "work on" in normalized or "week 1" in normalized or "impact" in normalized:
        return {
            "answer": "For week 1, start with billing issue #412 or notifications issue #89. The team guide marks billing and notifications as safe zones, and GitLab shows both as open good-first issues.",
            "sources": ["GitLab activity", "Team guide"],
            "action": None,
        }

    if "standup" in normalized or "shouldn't say" in normalized or "sensitive" in normalized:
        return {
            "answer": "Do not bring up GraphQL history in public, and avoid relitigating the v1 to v2 API migration. Per the team guide, Tuesday standup is recorded on Loom, so keep sensitive technical debate out of that forum.",
            "sources": ["Team guide"],
            "action": None,
        }

    if "merged fast" in normalized or "ship" in normalized or "pr" in normalized:
        return {
            "answer": "Use the PR template, tag Marcus for auth or payments, and tag Dev for infra or backend. Marcus averages about 2 hours for auth/payments reviews, but Friday deploys still require explicit +1 from Marcus or Dev.",
            "sources": ["GitLab activity", "Team guide"],
            "action": None,
        }

    if "meetings" in normalized or "matter" in normalized:
        return {
            "answer": "Thursday's eng retro is the meeting that actually matters for team sync. Tuesday standup is performative and recorded on Loom; Priya's Thursday 1:1 is the right venue for strategic issues.",
            "sources": ["Team guide"],
            "action": None,
        }

    if "understand" in normalized or "codebase" in normalized:
        files = ", ".join(context["activity"]["high_churn_files"])
        return {
            "answer": f"Start with the highest-churn files: {files}. Then talk to Marcus for auth and billing context, and Dev for infra/deploy context.",
            "sources": ["GitLab activity", "Team guide"],
            "action": None,
        }

    return {
        "answer": "Start in billing or notifications. The team guide marks both as safe zones, and GitLab shows billing issue #412 and notifications issue #89 as good first tasks.",
        "sources": ["GitLab activity", "Team guide"],
        "action": None,
    }
