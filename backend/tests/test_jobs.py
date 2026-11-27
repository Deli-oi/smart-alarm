import json

from app.jobs import run_daily_issue
from app.store import InMemoryStore
from tests.test_api import make_issue


async def test_daily_job_builds_once():
    store = InMemoryStore()
    calls = []

    async def complete(prompt: str) -> str:
        calls.append(prompt)
        if prompt.startswith("Find today"):
            return "Gospel: Lk 1:1 text"
        return json.dumps(make_issue("2026-11-27").model_dump())

    assert await run_daily_issue("2026-11-27", store, complete) is True
    assert (await store.get_issue("2026-11-27")).date == "2026-11-27"
    n = len(calls)
    assert await run_daily_issue("2026-11-27", store, complete) is False  # already built
    assert len(calls) == n
