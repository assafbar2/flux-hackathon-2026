from services.gitlab_mcp import GitLabMcpClient, normalize_demo_issue


def test_fetch_activity_uses_glab_mcp_issue_tool(monkeypatch):
    calls = []

    class FakeToolClient:
        def call_tool(self, name, arguments):
            calls.append((name, arguments))
            assert name == "glab_issue_list"
            return (
                "Showing 2 open issues in assafbar-group/flux-demo that match your search. (Page 1)\n\n"
                "ID\tTitle\tLabels\tCreated at\n"
                "#3\t[auth/P1] SSO migration blocked on Okta vendor response\t(P1, auth)\tabout 1 hour ago\n"
                "#1\t[billing/#412] Add invoice empty state\t(billing, good-first-issue)\tabout 1 hour ago\n"
            )

        def list_tool_names(self):
            return ["glab_issue_list", "glab_api"]

    monkeypatch.setenv("GITLAB_TOKEN", "demo-token")
    client = GitLabMcpClient(
        project_url="https://gitlab.com/assafbar-group/flux-demo",
        mcp_client=FakeToolClient(),
    )

    activity = client.fetch_demo_activity()

    assert calls[0][1]["flags"]["repo"] == "assafbar-group/flux-demo"
    assert activity["mcp_tools"] == ["glab_issue_list", "glab_api"]
    assert activity["issues"][0]["id"] == "412"
    assert activity["issues"][0]["project"] == "billing"
    assert activity["issues"][1]["project"] == "auth"


def test_assign_demo_issue_calls_glab_mcp_update(monkeypatch):
    calls = []

    class FakeToolClient:
        def call_tool(self, name, arguments):
            calls.append((name, arguments))
            if name == "glab_issue_list":
                return (
                    "ID\tTitle\tLabels\tCreated at\n"
                    "#1\t[billing/#412] Add invoice empty state\t(billing, good-first-issue)\tabout 1 hour ago\n"
                )
            if name == "glab_issue_update":
                return "Updated issue #1"
            raise AssertionError(name)

        def list_tool_names(self):
            return ["glab_issue_list", "glab_issue_update"]

    monkeypatch.setenv("GITLAB_TOKEN", "demo-token")
    client = GitLabMcpClient(
        project_url="https://gitlab.com/assafbar-group/flux-demo",
        mcp_client=FakeToolClient(),
    )

    assigned = client.assign_demo_issue(project="billing", issue_id="412", username="assafbar")

    assert calls[-1] == (
        "glab_issue_update",
        {
            "args": ["https://gitlab.com/assafbar-group/flux-demo/-/issues/1"],
            "flags": {"assignee": ["assafbar"]},
            "limit": 20000,
        },
    )
    assert assigned["gitlab_url"] == "https://gitlab.com/assafbar-group/flux-demo/-/issues/1"
    assert assigned["mcp_tool"] == "glab_issue_update"


def test_project_path_is_url_encoded():
    client = GitLabMcpClient(
        token="token",
        project_url="https://gitlab.com/assafbar-group/flux-demo",
    )

    assert client.encoded_project_path == "assafbar-group%2Fflux-demo"


def test_find_issue_by_demo_id_matches_title_marker():
    class FakeToolClient:
        def call_tool(self, name, arguments):
            return (
                "ID\tTitle\tLabels\tCreated at\n"
                "#1\t[billing/#412] Add invoice empty state\t(good-first-issue, billing)\tabout 1 hour ago\n"
            )

        def list_tool_names(self):
            return ["glab_issue_list"]

    client = GitLabMcpClient(
        project_url="https://gitlab.com/group/project",
        mcp_client=FakeToolClient(),
    )

    issue = client.find_issue_by_demo_id("billing", "412")

    assert issue["iid"] == 1


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
    class FakeToolClient:
        def call_tool(self, name, arguments):
            return (
                "ID\tTitle\tLabels\tCreated at\n"
                "#1\t[billing/#412] Add invoice empty state\t(good-first-issue, billing)\tabout 1 hour ago\n"
            )

        def list_tool_names(self):
            return ["glab_issue_list"]

    client = GitLabMcpClient(
        project_url="https://gitlab.com/group/project",
        mcp_client=FakeToolClient(),
    )

    activity = client.fetch_demo_activity()

    assert activity["issues"][0]["id"] == "412"
    assert activity["issues"][0]["project"] == "billing"
