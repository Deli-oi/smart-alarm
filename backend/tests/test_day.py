from datetime import date

from app.sources.calendar_ics import parse_day
from app.sources.gmail_imap import _fetch

ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//t//t//EN
BEGIN:VEVENT
UID:a@t
DTSTART;TZID=America/New_York:20261127T120000
DTEND;TZID=America/New_York:20261127T133000
SUMMARY:Work
END:VEVENT
BEGIN:VEVENT
UID:b@t
DTSTART;TZID=America/New_York:20261127T123000
DTEND;TZID=America/New_York:20261127T140000
SUMMARY:Council
END:VEVENT
BEGIN:VEVENT
UID:c@t
DTSTART;TZID=America/New_York:20261127T080000
DTEND;TZID=America/New_York:20261127T093000
RRULE:FREQ=DAILY
SUMMARY:Standup
END:VEVENT
BEGIN:VEVENT
UID:d@t
DTSTART;VALUE=DATE:20261125
DTEND;VALUE=DATE:20261129
SUMMARY:Trip
END:VEVENT
END:VCALENDAR
"""


def test_parse_day_flags_overlap_and_expands_recurrence():
    ev = parse_day(ICS, date(2026, 11, 27), "America/New_York")
    titles = [e.title for e in ev]
    assert titles == ["Trip", "Standup", "Work", "Council"]  # all-day first, then by time
    by = {e.title: e for e in ev}
    assert by["Work"].overlaps and by["Council"].overlaps
    assert not by["Standup"].overlaps
    assert by["Trip"].all_day


class FakeIMAP:
    def __init__(self, host): pass
    def login(self, u, p): assert (u, p) == ("me@x.com", "pw")
    def select(self, box, readonly=False): assert readonly
    def search(self, *a): return "OK", [b"1 2"]
    def fetch(self, i, spec):
        subj = {b"1": "First", b"2": "Second"}[i]
        return "OK", [(b"", f"From: Bob <b@x.com>\r\nSubject: {subj}\r\n\r\n".encode())]
    def logout(self): pass


def test_imap_newest_first_and_readonly():
    items = _fetch("me@x.com", "pw", 5, imap_cls=FakeIMAP)
    assert [i.subject for i in items] == ["Second", "First"]


class FakeSentIMAP(FakeIMAP):
    def select(self, box, readonly=False): assert "Sent" in box
    def search(self, *a): return "OK", [b"7"]
    def fetch(self, i, spec):
        h = "Subject: Re: Interview\r\nDate: Thu, 26 Nov 2026 20:00:00 -0500\r\nMessage-ID: <m7@x>\r\n\r\n"
        return "OK", [(b"", h.encode())]


async def test_sent_adapter_returns_recent_sent_mail():
    from app.sources.gmail_imap import GmailSentAdapter

    a = GmailSentAdapter("me@x.com", "pw", imap_cls=FakeSentIMAP)
    recs = await a.fetch_since("2026-11-26T12:00:00Z")
    assert [r.text for r in recs] == ["Re: Interview"] and recs[0].source == "gmail"
    assert await a.fetch_since("2026-11-27T12:00:00Z") == []


async def test_day_endpoint_serves_automation_plan(monkeypatch):
    from fastapi.testclient import TestClient

    from app import main
    from app.config import get_settings
    from app.store import InMemoryStore

    s = get_settings()
    monkeypatch.setattr(s, "ics_url", "")
    monkeypatch.setattr(s, "gmail_user", "")
    store = InMemoryStore()
    await store.save_day(main.today(), {"events": [{"start": "08:00", "end": "09:00", "title": "X", "all_day": False}], "mail": [{"sender": "a", "subject": "b"}]})
    main.app.dependency_overrides[main.get_store] = lambda: store
    try:
        r = TestClient(main.app).get("/day", headers={"Authorization": f"Bearer {s.api_token}"})
    finally:
        main.app.dependency_overrides.clear()
    j = r.json()
    assert j["source"] == "automation" and j["events"][0]["title"] == "X" and j["errors"] == []
