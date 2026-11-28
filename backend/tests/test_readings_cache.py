"""Readings are fetched server-side and kept in the database.

A scheduled Claude run that visits a website has to ask for approval, and at 5:37 in the
morning nobody answers, so the run hangs. The backend has no such problem: it fetches once
and the automation reads the result out of the database.
"""

import pytest
from fastapi.testclient import TestClient

from app import main
from app.store import InMemoryStore

HEADERS = {"Authorization": "Bearer testtok"}
SECTIONS = [{"label": "Gospel", "reference": "Luke 21:34-36", "text": "Stay alert."}]


def _client(store):
    main.app.dependency_overrides[main.get_store] = lambda: store
    return TestClient(main.app)


@pytest.fixture()
def store(monkeypatch):
    monkeypatch.setattr(main.get_settings(), "api_token", "testtok")
    s = InMemoryStore()
    yield s
    main.app.dependency_overrides.clear()


def test_stored_readings_are_served_without_touching_the_feed(store, monkeypatch):
    async def _boom(*a, **k):
        raise AssertionError("the feed must not be fetched when readings are already stored")

    monkeypatch.setattr("app.sources.usccb.fetch_sections", _boom)
    import asyncio

    asyncio.run(store.save_readings(main.today(), SECTIONS))
    body = _client(store).get("/readings/today", headers=HEADERS).json()
    assert body["source"] == "stored"
    assert body["sections"] == SECTIONS


def test_a_miss_fetches_once_and_keeps_it(store, monkeypatch):
    calls: list[int] = []

    async def _fetch(day, url=None):
        calls.append(1)
        return SECTIONS

    monkeypatch.setattr("app.sources.usccb.fetch_sections", _fetch)
    c = _client(store)
    assert c.get("/readings/today", headers=HEADERS).json()["source"] == "fetched"
    assert c.get("/readings/today", headers=HEADERS).json()["source"] == "stored"
    assert len(calls) == 1  # the second request is served from the database


def test_an_unreachable_feed_is_a_503_not_a_crash(store, monkeypatch):
    async def _down(day, url=None):
        raise RuntimeError("feed timed out")

    monkeypatch.setattr("app.sources.usccb.fetch_sections", _down)
    r = _client(store).get("/readings/today", headers=HEADERS)
    assert r.status_code == 503
    assert "feed timed out" in r.json()["detail"]


def test_the_archive_lists_every_issue_newest_first(store):
    from app.seed import demo_issue

    import asyncio

    for d in ("2026-11-26", "2026-11-28", "2026-11-27"):
        issue = demo_issue(d)
        asyncio.run(store.save_issue(issue))
    c = _client(store)
    rows = c.get("/issues", headers=HEADERS).json()
    assert [r["date"] for r in rows] == ["2026-11-28", "2026-11-27", "2026-11-26"]
    assert rows[0]["titles"]

    one = c.get("/issue/2026-11-26", headers=HEADERS).json()
    assert one["date"] == "2026-11-26"
    assert c.get("/issue/1999-01-01", headers=HEADERS).status_code == 404
