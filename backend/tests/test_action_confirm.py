from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_confirm_assign_issue_returns_success_without_chat_side_effect():
    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "glpat-demo",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    ).json()

    chat = client.post(
        "/api/chat",
        json={
            "workspace_id": setup["workspace_id"],
            "message": "Can you assign issue #412 to me?",
        },
    ).json()

    response = client.post(
        "/api/action/confirm",
        json={
            "workspace_id": setup["workspace_id"],
            "action": chat["action"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["gitlab_url"].endswith("/billing/-/issues/412")
    assert "assigned" in payload["message"]
