"""10:30pm check: decide what is still undone, using evidence from the sources."""

import re

from .models import Task
from .sources.base import SourceRecord


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3}


def evidence_for(task: Task, records: list[SourceRecord], min_overlap: int = 2) -> SourceRecord | None:
    """A record counts as evidence if it shares enough distinctive words with the task title."""
    want = _words(task.title)
    if not want:
        return None
    best: tuple[int, SourceRecord] | None = None
    for r in records:
        overlap = len(want & _words(r.text))
        if overlap >= min(min_overlap, len(want)) and (best is None or overlap > best[0]):
            best = (overlap, r)
    return best[1] if best else None


def leftover_tasks(tasks: list[Task], records: list[SourceRecord]) -> tuple[list[Task], list[Task]]:
    """Returns (leftover, auto_done). Tasks already done or pushed are ignored.

    Auto-done tasks are marked done with the source named in `source`; the user can still
    override each one in the app.
    """
    leftover: list[Task] = []
    auto_done: list[Task] = []
    for t in tasks:
        if t.status != "open":
            continue
        hit = evidence_for(t, records)
        if hit:
            auto_done.append(t.model_copy(update={"status": "done", "source": hit.source}))
        else:
            leftover.append(t)
    return leftover, auto_done


def notification_text(leftover: list[Task], auto_done: list[Task]) -> str:
    if not leftover:
        return f"All clear. {len(auto_done)} done."
    names = ", ".join(t.title for t in leftover[:3])
    more = f" and {len(leftover) - 3} more" if len(leftover) > 3 else ""
    return f"{len(leftover)} left: {names}{more}. {len(auto_done)} detected done."
