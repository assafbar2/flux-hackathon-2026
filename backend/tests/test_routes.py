from fastapi.testclient import TestClient

import main
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
    assert "SSO migration P1" in brief["now"]["body"]
    assert "blocked on Okta" in brief["now"]["body"]
    assert "Do not touch /auth" in brief["now"]["body"]
    assert "Marcus reviewed 71%" in brief["people"]["body"]
    assert "Sarah is on parental leave" in brief["people"]["body"]
    assert "Priya is 80% focused" in brief["people"]["body"]
    assert "Dev owns infra/CI" in brief["people"]["body"]
    assert "billing/#412" in brief["moves"]["body"]
    assert "notifications/#89" in brief["moves"]["body"]
    assert "GraphQL" in brief["landmines"]["body"]
    assert "#eng-general" in brief["landmines"]["body"]
    assert "PR template is mandatory" in brief["landmines"]["body"]


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


def test_health_returns_mode_and_version(monkeypatch):
    monkeypatch.setenv("FLUX_AGENT_MODE", "live")

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "mode": "live",
        "version": "1.0.0",
    }


def test_favicon_serves_svg_from_static_dir(monkeypatch, tmp_path):
    favicon = tmp_path / "favicon.svg"
    favicon.write_text("<svg aria-label=\"Flux\"></svg>", encoding="utf-8")
    monkeypatch.setattr(main, "STATIC_DIR", tmp_path)

    response = client.get("/favicon.svg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "aria-label=\"Flux\"" in response.text
