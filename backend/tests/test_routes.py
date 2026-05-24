from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_setup_returns_workspace_and_hire_link():
    response = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_id"]
    assert payload["hire_link"].endswith(f"/onboard/{payload['workspace_id']}")


def test_brief_returns_four_flux_sections():
    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    ).json()

    response = client.get(f"/api/brief/{setup['workspace_id']}")

    assert response.status_code == 200
    brief = response.json()["brief"]
    assert set(brief.keys()) == {"now", "people", "moves", "landmines"}
    assert "SSO migration" in brief["now"]["body"]
    assert "Marcus" in brief["people"]["body"]


def test_chat_returns_answer_with_sources():
    setup = client.post(
        "/api/setup",
        json={
            "gitlab_token": "demo-token",
            "notion_url": "https://notion.so/demo-page",
            "gitlab_username": "newhire",
        },
    ).json()

    response = client.post(
        "/api/chat",
        json={
            "workspace_id": setup["workspace_id"],
            "message": "Who actually owns the auth system?",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Marcus" in payload["answer"]
    assert "GitLab activity" in payload["sources"]
    assert "Team guide" in payload["sources"]
