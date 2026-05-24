from services.notion_parser import parse_team_guide


def test_parser_returns_four_named_sections():
    guide = """
## The Team (Real Talk)
### Sarah Kim
- Availability: On parental leave until June 15, 2026

## Right Now (updated May 2026)
- **Good first issues:** billing/#412 (no assignee, clear spec)

## Unwritten Rules
- Don't ask "why didn't you use GraphQL?" in public
- Friday deploys require explicit +1 from Marcus OR Dev.

## How to Ship Here
- **Fastest reviewer:** Marcus — average 2hr turnaround
"""

    parsed = parse_team_guide(guide)

    assert set(parsed.keys()) == {"team", "right_now", "unwritten_rules", "how_to_ship"}
    assert "parental leave until June 15, 2026" in parsed["team"]
    assert "billing/#412" in parsed["right_now"]
    assert "GraphQL" in parsed["unwritten_rules"]
    assert "Marcus" in parsed["how_to_ship"]
