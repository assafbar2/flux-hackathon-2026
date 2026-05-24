SECTION_MAP = {
    "the team (real talk)": "team",
    "right now": "right_now",
    "unwritten rules": "unwritten_rules",
    "how to ship here": "how_to_ship",
}


def normalize_heading(line: str) -> str:
    heading = line.lstrip("#").strip().lower()
    if heading.startswith("right now"):
        return "right now"
    return heading


def parse_team_guide(content: str) -> dict[str, str]:
    sections = {
        "team": "",
        "right_now": "",
        "unwritten_rules": "",
        "how_to_ship": "",
    }
    current_key: str | None = None
    collected: dict[str, list[str]] = {key: [] for key in sections}

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current_key = SECTION_MAP.get(normalize_heading(line))
            continue
        if current_key is not None:
            collected[current_key].append(line)

    return {key: "\n".join(value).strip() for key, value in collected.items()}
