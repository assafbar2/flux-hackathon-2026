from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def create_workspace() -> str:
    response = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    )
    return response.json()["workspace_id"]


def ask(workspace_id: str, message: str) -> dict:
    response = client.post(
        "/api/chat",
        json={"workspace_id": workspace_id, "message": message},
    )
    assert response.status_code == 200
    return response.json()


def test_demo_questions_return_grounded_answers():
    workspace_id = create_workspace()

    cases = [
        ("Who actually owns the auth system?", ["Based on GitLab activity", "Marcus", "71%"]),
        ("Who should I avoid pinging right now?", ["Per the team guide", "Sarah", "Priya"]),
        ("What should I work on to make an impact in week 1?", ["Based on GitLab activity", "#412", "#89"]),
        ("Is there anything I shouldn't say in standup?", ["Per the team guide", "GraphQL", "v1 to v2"]),
        ("How do I get a PR merged fast?", ["Based on GitLab activity", "PR template", "Friday"]),
        ("Which meetings actually matter?", ["Per the team guide", "Thursday", "Tuesday"]),
        ("What's the fastest way to understand this codebase?", ["Based on GitLab activity", "auth/session.ts", "billing/invoices.ts"]),
    ]

    for question, expected_fragments in cases:
        answer = ask(workspace_id, question)["answer"]
        for fragment in expected_fragments:
            assert fragment in answer


def test_assignment_question_returns_action_without_executing_it():
    workspace_id = create_workspace()

    payload = ask(workspace_id, "Can you assign issue #412 to me?")

    assert payload["action"] == {
        "type": "assign_issue",
        "issue_id": "412",
        "project": "billing",
        "username": "newhire",
    }
    assert "Confirm first" in payload["answer"]
