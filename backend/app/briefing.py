"""Jarvis day rundown script. Plain text, built from data; the voice is opt-in."""

from .models import Issue, Task


def build_briefing(day: str, tasks: list[Task], issue: Issue | None) -> str:
    lines = [f"Good morning. Here is your day for {day}."]
    if issue and issue.critical:
        lines.append("First, a critical item. " + " ".join(issue.critical))
    open_tasks = [t for t in tasks if t.status in ("open", "pushed")]
    if open_tasks:
        lines.append(f"You have {len(open_tasks)} things on your list.")
        for i, t in enumerate(open_tasks, 1):
            lines.append(f"{i}. {t.title}.")
    else:
        lines.append("Your task list is clear.")
    done = [t for t in tasks if t.status == "done"]
    if done:
        lines.append(f"{len(done)} done already.")
    return " ".join(lines)
