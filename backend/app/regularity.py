"""How consistent the mornings have been.

Sleep regularity, the day-to-day consistency of sleep and wake timing, predicts mortality more
strongly than sleep duration does (Windred et al., Sleep 2024, n > 60,000). That inverts what
most sleep products measure. This app cannot see sleep, but it does see the minute he starts his
morning, and consistency of that is the closest honest proxy it has.

Reported as plain counts, not a score out of a hundred. An invented index would imply a precision
that one data point a day does not have.
"""

from datetime import date, datetime, timedelta
from statistics import median
from zoneinfo import ZoneInfo

WINDOW_DAYS = 14
ON_TIME_MINUTES = 30  # within half an hour of his own usual start counts as the same time


def _minutes(iso: str, tz: str) -> int | None:
    try:
        local = datetime.fromisoformat(iso).astimezone(ZoneInfo(tz))
    except Exception:
        return None
    return local.hour * 60 + local.minute


def window(today_iso: str, days: int = WINDOW_DAYS) -> list[str]:
    end = date.fromisoformat(today_iso)
    return [(end - timedelta(days=i)).isoformat() for i in range(days)]


def summarise(attempts: list[dict], today_iso: str, tz: str = "America/New_York") -> dict:
    """First attempt of each day is that morning's start. Later attempts are retries."""
    firsts: dict[str, int] = {}
    for a in attempts:
        at = a.get("at")
        if not at:
            continue
        m = _minutes(at, tz)
        if m is None:
            continue
        d = a["date"]
        if d not in firsts or m < firsts[d]:
            firsts[d] = m

    days = window(today_iso)
    starts = [firsts[d] for d in days if d in firsts]
    out: dict = {
        "window_days": len(days),
        "mornings": len(starts),
        "run": 0,
        "usual": "",
        "on_time": 0,
        "spread_minutes": 0,
    }
    if not starts:
        return out

    # the current run of consecutive days, counting back from today
    for d in days:
        if d in firsts:
            out["run"] += 1
        else:
            break

    mid = int(median(starts))
    out["usual"] = f"{mid // 60:02d}:{mid % 60:02d}"
    out["on_time"] = sum(1 for m in starts if abs(m - mid) <= ON_TIME_MINUTES)
    out["spread_minutes"] = max(starts) - min(starts)
    return out
