"""Job bodies with injected dependencies, so tests run without network or database."""

from .issue_builder import Completer, build_issue
from .store import Store

READINGS_PROMPT = (
    "Find today's ({day}) Catholic daily Mass readings on the USCCB site (bible.usccb.org). "
    "Reply with each reading's label, scripture reference and full text, nothing else."
)


async def run_daily_issue(day: str, store: Store, complete: Completer) -> bool:
    """6:00 job. Returns True if a new issue was built, False if one already exists."""
    if await store.get_issue(day) is not None:
        return False
    readings = await complete(READINGS_PROMPT.format(day=day))
    issue = await build_issue(day, readings, complete)
    await store.save_issue(issue)
    return True
