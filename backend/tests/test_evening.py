import httpx

from app.evening import leftover_tasks, notification_text
from app.models import Task
from app.sources.base import SourceRecord
from app.sources.github import GitHubAdapter, parse_events

EVENTS = [
    {
        "type": "PushEvent",
        "created_at": "2026-11-27T20:00:00Z",
        "repo": {"name": "Deli-oi/smart-alarm"},
        "payload": {"commits": [{"sha": "abc", "message": "Add recall gate tests\n\nbody"}]},
    },
    {"type": "WatchEvent", "created_at": "2026-11-27T21:00:00Z", "repo": {"name": "x/y"}, "payload": {}},
    {
        "type": "PushEvent",
        "created_at": "2026-11-26T01:00:00Z",
        "repo": {"name": "old/repo"},
        "payload": {"commits": [{"sha": "old", "message": "ancient"}]},
    },
]


def test_parse_events_filters_type_and_time():
    recs = parse_events(EVENTS, "2026-11-27T00:00:00Z")
    assert [r.external_id for r in recs] == ["abc"]
    assert recs[0].text == "Deli-oi/smart-alarm: Add recall gate tests"


def task(i: str, title: str, status: str = "open") -> Task:
    return Task(id=i, date="2026-11-27", title=title, status=status)


def test_commit_marks_matching_task_done():
    recs = parse_events(EVENTS, "2026-11-27T00:00:00Z")
    tasks = [task("1", "Write recall gate tests"), task("2", "Call the dentist")]
    left, done = leftover_tasks(tasks, recs)
    assert [t.id for t in left] == ["2"]
    assert done[0].id == "1" and done[0].status == "done" and done[0].source == "github"


def test_done_and_pushed_tasks_are_ignored():
    left, done = leftover_tasks([task("1", "x thing", "done"), task("2", "y thing", "pushed")], [])
    assert left == [] and done == []


def test_short_titles_need_full_match():
    recs = [SourceRecord(source="gmail", external_id="m", when="t", text="Re: invoice from vendor")]
    left, done = leftover_tasks([task("1", "Pay invoice")], recs)
    assert [t.id for t in done] == ["1"]


def test_notification_text():
    assert notification_text([], [task("1", "a")]) == "All clear. 1 done."
    text = notification_text([task(str(i), f"task{i}") for i in range(5)], [])
    assert "5 left" in text and "and 2 more" in text


async def test_adapter_uses_injected_client():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer tok"
        return httpx.Response(200, json=EVENTS)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    recs = await GitHubAdapter("Deli-oi", "tok", client).fetch_since("2026-11-27T00:00:00Z")
    assert len(recs) == 1


async def test_evening_job_marks_done_and_saves_summary():
    from app.jobs import run_evening_check
    from app.store import InMemoryStore

    store = InMemoryStore()
    await store.put_task(task("1", "Write recall gate tests"))
    await store.put_task(task("2", "Call the dentist"))

    class Fake:
        name = "fake"

        async def fetch_since(self, since):
            return parse_events(EVENTS, "2026-11-27T00:00:00Z")

    class Broken:
        name = "broken"

        async def fetch_since(self, since):
            raise RuntimeError("down")

    text = await run_evening_check("2026-11-27", "x", store, [Broken(), Fake()])
    assert (await store.get_task("1")).status == "done"
    assert (await store.get_task("2")).status == "open"
    assert await store.get_summary("2026-11-27") == text and "1 left" in text
