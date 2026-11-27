"""Job bodies with injected dependencies, so tests run without network or database."""

from .issue_builder import Completer, build_issue
from .store import Store

READINGS_PROMPT = (
    "Find today's ({day}) Catholic daily Mass readings on the USCCB site (bible.usccb.org). "
    "Reply with each reading's label, scripture reference and full text, nothing else."
)


async def run_daily_issue(day: str, store: Store, complete: Completer, fetch_readings=None) -> bool:
    """6:00 job. Returns True if a new issue was built, False if one already exists.

    `fetch_readings(day) -> text` is tried first (the USCCB feed); if it fails or is absent,
    Claude is asked to find the readings with web search.
    """
    if await store.get_issue(day) is not None:
        return False
    readings = None
    if fetch_readings is not None:
        try:
            readings = await fetch_readings(day)
        except Exception:
            readings = None
    if not readings:
        readings = await complete(READINGS_PROMPT.format(day=day))
    issue = await build_issue(day, readings, complete)
    await store.save_issue(issue)
    return True


async def run_evening_check(day: str, since_iso: str, store: Store, adapters: list) -> str:
    """10:30pm job: pull evidence, auto-mark done tasks, save the summary the app shows."""
    from .evening import leftover_tasks, notification_text

    records = []
    for a in adapters:
        try:
            records += await a.fetch_since(since_iso)
        except Exception:  # one broken source must not sink the whole check
            continue
    tasks = await store.list_tasks(day)
    leftover, auto_done = leftover_tasks(tasks, records)
    for t in auto_done:
        await store.put_task(t)
    text = notification_text(leftover, auto_done)
    await store.save_summary(day, text)
    return text
