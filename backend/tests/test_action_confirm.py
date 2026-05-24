from fastapi.testclient import TestClient

import routes.action
from main import app


client = TestClient(app)


def test_confirm_assign_issue_returns_success_without_chat_side_effect(monkeypatch):
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    monkeypatch.delenv("GITLAB_PROJECT_URL", raising=False)

    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
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


def test_confirm_assign_issue_uses_live_gitlab_when_configured(monkeypatch):
    class FakeGitLabClient:
        def assign_demo_issue(self, *, project, issue_id, username):
            assert project == "billing"
            assert issue_id == "412"
            assert username == "assafbar"
            return {
                "iid": 1,
                "gitlab_url": "https://gitlab.com/assafbar-group/flux-demo/-/issues/1",
            }

    monkeypatch.setenv("GITLAB_TOKEN", "token")
    monkeypatch.setenv("GITLAB_PROJECT_URL", "https://gitlab.com/assafbar-group/flux-demo")
    monkeypatch.setattr(routes.action, "GitLabMcpClient", FakeGitLabClient)

    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "assafbar",
        },
    ).json()

    response = client.post(
        "/api/action/confirm",
        json={
            "workspace_id": setup["workspace_id"],
            "action": {
                "type": "assign_issue",
                "issue_id": "412",
                "project": "billing",
                "username": "assafbar",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["gitlab_url"] == "https://gitlab.com/assafbar-group/flux-demo/-/issues/1"


def test_confirm_assign_issue_replaces_placeholder_username_with_config(monkeypatch):
    class FakeGitLabClient:
        def assign_demo_issue(self, *, project, issue_id, username):
            assert username == "assafbar"
            return {
                "iid": 1,
                "gitlab_url": "https://gitlab.com/assafbar-group/flux-demo/-/issues/1",
            }

    monkeypatch.setenv("GITLAB_TOKEN", "token")
    monkeypatch.setenv("GITLAB_PROJECT_URL", "https://gitlab.com/assafbar-group/flux-demo")
    monkeypatch.setenv("GITLAB_USERNAME", "assafbar")
    monkeypatch.setattr(routes.action, "GitLabMcpClient", FakeGitLabClient)

    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    ).json()

    response = client.post(
        "/api/action/confirm",
        json={
            "workspace_id": setup["workspace_id"],
            "action": {
                "type": "assign_issue",
                "issue_id": "412",
                "project": "billing",
                "username": "newhire",
            },
        },
    )

    assert response.status_code == 200
