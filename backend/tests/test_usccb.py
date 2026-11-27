import html
from datetime import date

import pytest

from app.jobs import run_daily_issue
from app.sources.usccb import format_for_prompt, pick_readings
from app.store import InMemoryStore

DESC = (
    '<h4>Reading 1 <a href="x">Revelation 20:1-4</a></h4><div class="poetry"><p>Line one<br>Line two</p>'
    '<p>&nbsp;</p></div><h4>Responsorial Psalm <a href="y">Psalm 84:3</a></h4>'
    '<div class="poetry"><p>Refrain <strong>R.</strong><br>Verse</p></div>'
    '<h4>Gospel <a href="z">Luke 21:29-33</a></h4><div class="poetry"><p>Gospel text<br>more</p></div>'
)
FEED = f"""<?xml version="1.0"?><rss><channel>
<item><title>Nav only</title><link>https://bible.usccb.org/bible/readings/112726.cfm</link><description>{html.escape('<a href="x">links</a>')}</description></item>
<item><title>Friday</title><link>https://bible.usccb.org/bible/readings/112726.cfm</link><description>{html.escape(DESC)}</description></item>
<item><title>Thursday</title><link>https://bible.usccb.org/bible/readings/112626.cfm</link><description>{html.escape(DESC)}</description></item>
</channel></rss>"""


def test_picks_the_item_with_text_and_parses_sections():
    secs = pick_readings(FEED, date(2026, 11, 27))
    assert [s["label"] for s in secs] == ["Reading 1", "Responsorial Psalm", "Gospel"]
    assert secs[0]["reference"] == "Revelation 20:1-4" and "Line one\nLine two" in secs[0]["text"]
    assert "Luke 21:29-33" in format_for_prompt(secs)


def test_missing_day_raises():
    with pytest.raises(LookupError):
        pick_readings(FEED, date(2026, 12, 25))


async def test_job_uses_feed_then_falls_back_to_claude():
    prompts = []

    async def complete(p):
        prompts.append(p)
        raise RuntimeError("stop after readings decision")

    async def feed_ok(day):
        return "FEED READINGS"

    async def feed_bad(day):
        raise RuntimeError("down")

    for feed, expect_claude_for_readings in ((feed_ok, False), (feed_bad, True)):
        prompts.clear()
        with pytest.raises(Exception):
            await run_daily_issue("2026-11-27", InMemoryStore(), complete, fetch_readings=feed)
        asked_readings = any(p.startswith("Find today") for p in prompts)
        assert asked_readings is expect_claude_for_readings
