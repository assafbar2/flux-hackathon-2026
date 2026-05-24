from services.notion import block_to_markdown, extract_page_id


def test_extract_page_id_from_notion_url():
    page_id = extract_page_id(
        "https://www.notion.so/assafbarnir/Hew-Hired-6-2-2026-36a19505465b80ed88aad950ee71264d"
    )

    assert page_id == "36a19505-465b-80ed-88aa-d950ee71264d"


def test_block_to_markdown_supports_headings_and_paragraphs():
    heading = {
        "type": "heading_2",
        "heading_2": {"rich_text": [{"plain_text": "Right Now"}]},
    }
    paragraph = {
        "type": "paragraph",
        "paragraph": {"rich_text": [{"plain_text": "SSO migration is blocked."}]},
    }

    assert block_to_markdown(heading) == "## Right Now"
    assert block_to_markdown(paragraph) == "SSO migration is blocked."
