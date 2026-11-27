"""Calendar through Google's private iCal link. No OAuth: paste the link into ICS_URL."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import httpx
import icalendar
import recurring_ical_events
from pydantic import BaseModel


class Event(BaseModel):
    start: str  # HH:MM local, "" for all-day
    end: str
    title: str
    location: str = ""
    all_day: bool = False
    overlaps: bool = False


def parse_day(ics_text: str, day: date, tz: str) -> list[Event]:
    zone = ZoneInfo(tz)
    cal = icalendar.Calendar.from_ical(ics_text)
    start = datetime.combine(day, time.min, tzinfo=zone)
    out: list[Event] = []
    for ev in recurring_ical_events.of(cal).between(start, start + timedelta(days=1)):
        s, e = ev.get("DTSTART").dt, ev.get("DTEND").dt
        title = str(ev.get("SUMMARY", "Untitled"))
        loc = str(ev.get("LOCATION", ""))
        if not isinstance(s, datetime):  # all-day events are context, not schedule
            out.append(Event(start="", end="", title=title, location=loc, all_day=True))
            continue
        s, e = s.astimezone(zone), e.astimezone(zone)
        out.append(Event(start=s.strftime("%H:%M"), end=e.strftime("%H:%M"), title=title, location=loc))
    timed = sorted((x for x in out if not x.all_day), key=lambda x: x.start)
    for a in timed:
        a.overlaps = any(b is not a and a.start < b.end and b.start < a.end for b in timed)
    return [x for x in out if x.all_day] + timed


async def fetch_day(url: str, day: date, tz: str) -> list[Event]:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
        r = await c.get(url)
        r.raise_for_status()
    return parse_day(r.text, day, tz)
