"""The day's notes as one markdown file.

This is the hand-off: the app writes notes all day, and the evening run reads this file
and acts on it through the connectors. It is written to be read by a person too, so the
record of what was asked for is legible when something goes wrong.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from .models import Note, Task


def _local_time(iso: str, tz: str) -> str:
    try:
        return datetime.fromisoformat(iso).astimezone(ZoneInfo(tz)).strftime("%H:%M")
    except Exception:
        return iso[11:16] if len(iso) > 15 else iso


def day_log_markdown(day: str, notes: list[Note], tasks: list[Task], tz: str = "America/New_York") -> str:
    try:
        heading = date.fromisoformat(day).strftime("%A %-d %B %Y")
    except ValueError:
        heading = day
    out = [f"# Day log, {heading}", ""]

    if notes:
        out.append("## What he said")
        out.append("")
        for n in notes:
            label = "replied" if n.kind == "reply" else "note"
            out.append(f"- **{_local_time(n.at, tz)}** ({label}) {n.text}")
        out.append("")
    else:
        out += ["## What he said", "", "Nothing recorded today.", ""]

    if tasks:
        out.append("## Tasks as they stand")
        out.append("")
        for t in tasks:
            mark = "x" if t.status == "done" else " "
            note = f" — {t.note}" if t.note else ""
            out.append(f"- [{mark}] {t.title}{note}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"
