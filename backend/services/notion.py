import os
import re
from typing import Any

import httpx


NOTION_VERSION = "2026-03-11"


def extract_page_id(url_or_id: str) -> str:
    compact = url_or_id.replace("-", "")
    match = re.search(r"([0-9a-fA-F]{32})(?:[?#].*)?$", compact)
    if not match:
        raise ValueError("Notion page URL does not contain a page ID")
    raw = match.group(1)
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


def rich_text_to_plain_text(value: list[dict[str, Any]]) -> str:
    return "".join(part.get("plain_text", "") for part in value)


def block_to_markdown(block: dict[str, Any]) -> str:
    block_type = block.get("type")
    content = block.get(block_type, {})
    text = rich_text_to_plain_text(content.get("rich_text", []))

    if not text:
        return ""
    if block_type == "heading_1":
        return f"# {text}"
    if block_type == "heading_2":
        return f"## {text}"
    if block_type == "heading_3":
        return f"### {text}"
    if block_type in {"bulleted_list_item", "numbered_list_item", "to_do"}:
        return f"- {text}"
    if block_type == "paragraph":
        return text
    return text


class NotionClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("NOTION_TOKEN", "")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def fetch_blocks(self, page_id: str) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            response = httpx.get(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=self._headers(),
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            for block in payload.get("results", []):
                blocks.append(block)
                if block.get("has_children"):
                    blocks.extend(self.fetch_blocks(block["id"]))
            if not payload.get("has_more"):
                return blocks
            cursor = payload.get("next_cursor")

    def fetch_page_markdown(self, page_url: str) -> str:
        page_id = extract_page_id(page_url)
        lines = [block_to_markdown(block) for block in self.fetch_blocks(page_id)]
        return "\n".join(line for line in lines if line)
