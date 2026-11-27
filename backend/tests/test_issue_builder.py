import json

import pytest

from app.issue_builder import build_issue, parse_issue
from tests.test_api import make_issue


def fake_reply(day: str) -> str:
    return "Here you go:\n" + json.dumps(make_issue(day).model_dump())


async def test_parse_extracts_json_from_chatty_reply():
    issue = parse_issue(fake_reply("2026-11-27"))
    assert issue.date == "2026-11-27" and len(issue.articles) == 3


async def test_build_retries_after_bad_reply():
    replies = ["not json at all", fake_reply("2026-11-27")]

    async def complete(prompt: str) -> str:
        return replies.pop(0)

    issue = await build_issue("2026-11-27", "readings", complete)
    assert len(issue.questions) == 10


async def test_build_gives_up_after_retries():
    async def complete(prompt: str) -> str:
        return "nope"

    with pytest.raises(RuntimeError):
        await build_issue("2026-11-27", "readings", complete, retries=1)


def test_issue_length_is_about_a_15_minute_read():
    words = make_issue("2026-11-27").word_count()
    assert 1500 < words < 3500
