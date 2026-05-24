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

    assert "Marcus" in ask(workspace_id, "Who actually owns the auth system?")["answer"]
    assert "Sarah" in ask(workspace_id, "Who should I avoid pinging right now?")["answer"]
    assert "#412" in ask(workspace_id, "What should I work on to make an impact in week 1?")["answer"]
    assert "GraphQL" in ask(workspace_id, "Is there anything I shouldn't say in standup?")["answer"]
    assert "PR template" in ask(workspace_id, "How do I get a PR merged fast?")["answer"]
    assert "Thursday" in ask(workspace_id, "Which meetings actually matter?")["answer"]
    assert "auth/session.ts" in ask(workspace_id, "What's the fastest way to understand this codebase?")["answer"]


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
