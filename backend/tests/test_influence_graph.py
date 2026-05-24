from services.influence_graph import build_influence_graph


def test_influence_graph_identifies_owners_and_good_first_issues():
    activity = {
        "merge_requests": [
            {"area": "auth", "reviewer": "Marcus", "review_hours": 2},
            {"area": "auth", "reviewer": "Marcus", "review_hours": 2},
            {"area": "auth", "reviewer": "Marcus", "review_hours": 3},
            {"area": "auth", "reviewer": "Dev", "review_hours": 4},
            {"area": "infra", "reviewer": "Dev", "review_hours": 4},
            {"area": "infra", "reviewer": "Dev", "review_hours": 5},
        ],
        "issues": [
            {
                "id": "412",
                "project": "billing",
                "title": "Add invoice empty state",
                "labels": ["good-first-issue"],
                "assignee": None,
                "state": "opened",
            },
            {
                "id": "88",
                "project": "auth",
                "title": "SSO migration blocked",
                "labels": ["P1"],
                "assignee": "Marcus",
                "state": "opened",
            },
        ],
    }

    graph = build_influence_graph(activity)

    assert graph["owners"]["auth"]["owner"] == "Marcus"
    assert graph["owners"]["auth"]["review_share"] == 0.75
    assert graph["owners"]["infra"]["owner"] == "Dev"
    assert graph["fastest_reviewers"][0]["reviewer"] == "Marcus"
    assert graph["good_first_issues"][0]["id"] == "412"
    assert graph["active_fires"][0]["id"] == "88"
