from services import demo_intelligence


def test_live_notion_text_is_used_when_available(monkeypatch):
    class FakeNotionClient:
        def __init__(self, token):
            self.token = token

        def fetch_page_markdown(self, page_url):
            assert page_url == "https://notion.so/example-1234567890abcdef1234567890abcdef"
            return "## The Team (Real Talk)\n### Marcus\n- Available"

    monkeypatch.setenv("NOTION_TOKEN", "notion-token-placeholder")
    monkeypatch.setenv("NOTION_PAGE_URL", "https://notion.so/example-1234567890abcdef1234567890abcdef")
    monkeypatch.setattr(demo_intelligence, "NotionClient", FakeNotionClient)

    text, source = demo_intelligence.load_team_guide_text()

    assert source == "live_notion"
    assert "Marcus" in text


def test_empty_live_notion_text_falls_back_to_fixture(monkeypatch):
    class EmptyNotionClient:
        def __init__(self, token):
            self.token = token

        def fetch_page_markdown(self, page_url):
            return ""

    monkeypatch.setenv("NOTION_TOKEN", "notion-token-placeholder")
    monkeypatch.setenv("NOTION_PAGE_URL", "https://notion.so/example-1234567890abcdef1234567890abcdef")
    monkeypatch.setattr(demo_intelligence, "NotionClient", EmptyNotionClient)

    text, source = demo_intelligence.load_team_guide_text()

    assert source == "fixture"
    assert "The Team (Real Talk)" in text


def test_live_gitlab_issues_replace_fixture_issues(monkeypatch):
    class FakeGitLabClient:
        def fetch_demo_activity(self):
            return {
                "issues": [
                    {
                        "id": "412",
                        "iid": 1,
                        "project": "billing",
                        "title": "[billing/#412] Add invoice empty state",
                        "labels": ["good-first-issue"],
                        "assignee": None,
                        "state": "opened",
                    }
                ]
            }

    monkeypatch.setenv("GITLAB_TOKEN", "token")
    monkeypatch.setenv("GITLAB_PROJECT_URL", "https://gitlab.com/group/project")
    monkeypatch.setattr(demo_intelligence, "GitLabMcpClient", FakeGitLabClient)

    activity = demo_intelligence.load_gitlab_activity()

    assert activity["issues"] == [
        {
            "id": "412",
            "iid": 1,
            "project": "billing",
            "title": "[billing/#412] Add invoice empty state",
            "labels": ["good-first-issue"],
            "assignee": None,
            "state": "opened",
        }
    ]
    assert activity["merge_requests"]
