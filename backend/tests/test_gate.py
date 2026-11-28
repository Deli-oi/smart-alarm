"""The lock, when it is switched on. Off by default: a false lock costs a morning."""

from fastapi.testclient import TestClient

from app import main
from app.store import InMemoryStore

HEADERS = {"Authorization": "Bearer testtok"}


def _client(store):
    main.app.dependency_overrides[main.get_store] = lambda: store
    return TestClient(main.app)


def test_day_is_open_when_the_gate_is_not_enforced(monkeypatch):
    s = main.get_settings()
    monkeypatch.setattr(s, "api_token", "testtok")
    monkeypatch.setattr(s, "enforce_gate", False)
    monkeypatch.setattr(s, "ics_url", "")
    try:
        assert _client(InMemoryStore()).get("/day", headers=HEADERS).status_code == 200
    finally:
        main.app.dependency_overrides.clear()


def test_enforced_gate_locks_the_day_until_recall_is_passed(monkeypatch):
    s = main.get_settings()
    monkeypatch.setattr(s, "api_token", "testtok")
    monkeypatch.setattr(s, "enforce_gate", True)
    monkeypatch.setattr(s, "ics_url", "")
    store = InMemoryStore()
    try:
        c = _client(store)
        assert c.get("/day", headers=HEADERS).status_code == 423
        assert c.get("/tasks/today", headers=HEADERS).status_code == 423

        await_day = main.today()
        store.attempts.append({"date": await_day, "score": 0.5, "passed": False})
        assert c.get("/day", headers=HEADERS).status_code == 423  # a failed attempt is not a pass

        store.attempts.append({"date": await_day, "score": 0.875, "passed": True})
        assert c.get("/day", headers=HEADERS).status_code == 200
        assert c.get("/tasks/today", headers=HEADERS).status_code == 200
    finally:
        main.app.dependency_overrides.clear()


def test_a_logged_skip_also_opens_the_day(monkeypatch):
    s = main.get_settings()
    monkeypatch.setattr(s, "api_token", "testtok")
    monkeypatch.setattr(s, "enforce_gate", True)
    monkeypatch.setattr(s, "ics_url", "")
    store = InMemoryStore()
    try:
        c = _client(store)
        assert c.get("/day", headers=HEADERS).status_code == 423
        c.post("/quiz/skip", json={"reason": "overslept"}, headers=HEADERS)
        assert c.get("/day", headers=HEADERS).status_code == 200
    finally:
        main.app.dependency_overrides.clear()
