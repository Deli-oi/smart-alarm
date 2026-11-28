"""Today's Mass readings from the USCCB RSS feed (bible.usccb.org/readings.rss).

Structure observed 2026-11-27: each item's description is entity-escaped HTML, one <h4> per
section (its <a> text is the citation) followed by <div class="poetry"> with the text. Items are
keyed by a link ending in MMDDYY.cfm; some feast days add navigation-only items with no text.
"""

import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser

import httpx

FEED = "https://bible.usccb.org/readings.rss"


class _Sections(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict] = []
        self._in_h4 = False
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        if tag == "h4":
            self._in_h4 = True
            self.sections.append({"label": "", "reference": "", "text": ""})
        elif tag == "a" and self._in_h4:
            self._in_a = True
        elif tag in ("br", "p") and self.sections and not self._in_h4:
            self.sections[-1]["text"] += "\n"

    def handle_endtag(self, tag):
        if tag == "h4":
            self._in_h4 = False
        elif tag == "a":
            self._in_a = False

    def handle_data(self, data):
        if not self.sections:
            return
        cur = self.sections[-1]
        if self._in_a:
            cur["reference"] += data
        elif self._in_h4:
            cur["label"] += data
        else:
            cur["text"] += data


def parse_item(description_html: str) -> list[dict]:
    p = _Sections()
    p.feed(description_html)
    out = []
    for s in p.sections:
        text = "\n".join(line.strip() for line in s["text"].replace("\xa0", " ").splitlines() if line.strip())
        if text:
            out.append({"label": s["label"].strip(), "reference": s["reference"].strip(), "text": text})
    return out


def pick_readings(feed_xml: str, day: date) -> list[dict]:
    """Sections for `day`. Raises LookupError when the feed has no readings for that date."""
    stamp = day.strftime("%m%d%y")
    root = ET.fromstring(feed_xml)
    best: list[dict] = []
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip()
        if link.endswith(f"{stamp}.cfm") or f"/{stamp}" in link:
            sections = parse_item(item.findtext("description") or "")
            if sum(len(s["text"]) for s in sections) > sum(len(s["text"]) for s in best):
                best = sections  # skip navigation-only items
    if not best:
        raise LookupError(f"no readings in feed for {day.isoformat()}")
    return best


def format_for_prompt(sections: list[dict]) -> str:
    return "\n\n".join(f"{s['label']} ({s['reference']})\n{s['text']}" for s in sections)


async def fetch_sections(day: date, url: str = FEED) -> list[dict]:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
        r = await c.get(url, headers={"User-Agent": "smart-alarm/0.1 (personal use)"})
        r.raise_for_status()
    return pick_readings(r.text, day)


async def fetch_readings_text(day: date, url: str = FEED) -> str:
    return format_for_prompt(await fetch_sections(day, url))
