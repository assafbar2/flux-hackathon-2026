import httpx

from services.gitlab_mcp import GitLabMcpClient, normalize_demo_issue


def test_project_path_is_url_encoded():
    client = GitLabMcpClient(
        token="token",
        project_url="https://gitlab.com/assafbar-group/flux-demo",
    )

    assert client.encoded_project_path == "assafbar-group%2Fflux-demo"


def test_find_issue_by_demo_id_matches_title_marker():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["PRIVATE-TOKEN"] == "token"
        return httpx.Response(
            200,
            json=[
                {
                    "iid": 1,
                    "title": "[billing/#412] Add invoice empty state",
                    "web_url": "https://gitlab.com/group/project/-/issues/1",
                }
            ],
        )

    client = GitLabMcpClient(
        token="token",
        project_url="https://gitlab.com/group/project",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    issue = client.find_issue_by_demo_id("billing", "412")

    assert issue["iid"] == 1


def test_assign_issue_uses_actual_iid_and_assignee_id():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/users"):
            return httpx.Response(200, json=[{"id": 42, "username": "assafbar"}])
        if request.url.path.endswith("/issues"):
            return httpx.Response(
                200,
                json=[
                    {
                        "iid": 1,
                        "title": "[billing/#412] Add invoice empty state",
                        "web_url": "https://gitlab.com/group/project/-/issues/1",
                    }
                ],
            )
        if request.url.path.endswith("/issues/1"):
            return httpx.Response(
                200,
                json={"iid": 1, "web_url": "https://gitlab.com/group/project/-/issues/1"},
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.url}")

    client = GitLabMcpClient(
        token="token",
        project_url="https://gitlab.com/group/project",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.assign_demo_issue(project="billing", issue_id="412", username="assafbar")

    assert result["gitlab_url"] == "https://gitlab.com/group/project/-/issues/1"
    assert any(request.method == "PUT" for request in requests)


def test_normalize_demo_issue_uses_title_marker_as_display_id():
    issue = normalize_demo_issue(
        {
            "iid": 1,
            "title": "[billing/#412] Add invoice empty state",
            "labels": ["good-first-issue", "billing"],
            "state": "opened",
            "assignees": [],
            "web_url": "https://gitlab.com/group/project/-/issues/1",
        }
    )

    assert issue["id"] == "412"
    assert issue["iid"] == 1
    assert issue["project"] == "billing"
    assert issue["assignee"] is None


def test_live_activity_normalizes_issues():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "iid": 1,
                    "title": "[billing/#412] Add invoice empty state",
                    "labels": ["good-first-issue", "billing"],
                    "state": "opened",
                    "assignees": [],
                    "web_url": "https://gitlab.com/group/project/-/issues/1",
                }
            ],
        )

    client = GitLabMcpClient(
        token="token",
        project_url="https://gitlab.com/group/project",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    activity = client.fetch_demo_activity()

    assert activity["issues"][0]["id"] == "412"
    assert activity["issues"][0]["project"] == "billing"
