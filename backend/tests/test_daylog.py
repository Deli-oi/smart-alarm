"""The day log: what he said, kept in order, and handed over as one markdown file."""

from fastapi.testclient import TestClient

from app import main
from app.daylog import day_log_markdown
from app.models import Note, Task
from app.store import InMemoryStore

HEADERS = {"Authorization": "Bearer testtok"}


def _client(store):
    main.app.dependency_overrides[main.get_store] = lambda: store
    return TestClient(main.app)


def test_notes_round_trip_and_markdown(monkeypatch):
    monkeypatch.setattr(main.get_settings(), "api_token", "testtok")
    store = InMemoryStore()
    try:
        c = _client(store)
        assert c.post("/notes", json={"text": "  move the gym to six  "}, headers=HEADERS).json()["text"] == "move the gym to six"
        c.post("/notes", json={"text": "draft a yes to Alyssa", "kind": "reply"}, headers=HEADERS)

        notes = c.get("/notes/today", headers=HEADERS).json()
        assert [n["text"] for n in notes] == ["move the gym to six", "draft a yes to Alyssa"]
        assert notes[0]["at"].endswith("+00:00")  # stamped by the server, in UTC

        md = c.get("/notes/today.md", headers=HEADERS)
        assert md.headers["content-type"].startswith("text/markdown")
        assert "move the gym to six" in md.text
        assert "(replied)" in md.text
    finally:
        main.app.dependency_overrides.clear()


def test_empty_text_is_rejected(monkeypatch):
    monkeypatch.setattr(main.get_settings(), "api_token", "testtok")
    try:
        assert _client(InMemoryStore()).post("/notes", json={"text": ""}, headers=HEADERS).status_code == 422
    finally:
        main.app.dependency_overrides.clear()


def test_process_now_flag(monkeypatch):
    monkeypatch.setattr(main.get_settings(), "api_token", "testtok")
    store = InMemoryStore()
    try:
        c = _client(store)
        assert c.get("/notes/pending", headers=HEADERS).json()["requested"] is False
        c.post("/notes/process-now", headers=HEADERS)
        assert c.get("/notes/pending", headers=HEADERS).json()["requested"] is True
    finally:
        main.app.dependency_overrides.clear()


def test_markdown_is_legible_without_notes():
    md = day_log_markdown("2026-11-28", [], [Task(id="t1", date="2026-11-28", title="Book the flight")])
    assert "Nothing recorded today." in md
    assert "- [ ] Book the flight" in md


def test_markdown_shows_local_time_and_done_tasks():
    notes = [Note(at="2026-11-28T13:05:00+00:00", text="call mom")]
    tasks = [Task(id="t1", date="2026-11-28", title="Ship it", status="done", note="commit")]
    md = day_log_markdown("2026-11-28", notes, tasks)
    assert "**08:05**" in md  # 13:05 UTC is 08:05 in New York
    assert "- [x] Ship it — commit" in md
