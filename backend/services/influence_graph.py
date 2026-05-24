from collections import defaultdict
from statistics import mean
from typing import Any


def build_influence_graph(activity: dict[str, Any]) -> dict[str, Any]:
    reviews_by_area: dict[str, list[dict[str, Any]]] = defaultdict(list)
    review_hours_by_person: dict[str, list[float]] = defaultdict(list)

    for merge_request in activity.get("merge_requests", []):
        area = merge_request["area"]
        reviewer = merge_request["reviewer"]
        reviews_by_area[area].append(merge_request)
        review_hours_by_person[reviewer].append(float(merge_request.get("review_hours", 0)))

    owners = {}
    for area, reviews in reviews_by_area.items():
        counts: dict[str, int] = defaultdict(int)
        for review in reviews:
            counts[review["reviewer"]] += 1
        owner, owner_count = max(counts.items(), key=lambda item: item[1])
        owners[area] = {
            "owner": owner,
            "review_count": owner_count,
            "total_reviews": len(reviews),
            "review_share": round(owner_count / len(reviews), 2),
        }

    fastest_reviewers = sorted(
        [
            {"reviewer": reviewer, "average_hours": round(mean(hours), 1)}
            for reviewer, hours in review_hours_by_person.items()
            if hours
        ],
        key=lambda item: item["average_hours"],
    )

    open_issues = [
        issue
        for issue in activity.get("issues", [])
        if issue.get("state") == "opened"
    ]
    good_first_issues = [
        issue
        for issue in open_issues
        if "good-first-issue" in issue.get("labels", []) and not issue.get("assignee")
    ]
    active_fires = [
        issue
        for issue in open_issues
        if any(label in {"P0", "P1"} for label in issue.get("labels", []))
    ]

    return {
        "owners": owners,
        "fastest_reviewers": fastest_reviewers,
        "good_first_issues": good_first_issues,
        "active_fires": active_fires,
    }
