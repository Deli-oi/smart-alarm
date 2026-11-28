"""The emergency skip has to leave a record, or the gate means nothing."""

from fastapi.testclient import TestClient

from app import main
from app.store import InMemoryStore

HEADERS = {"Authorization": "Bearer testtok"}


def _client(store: InMemoryStore) -> TestClient:
    main.app.dependency_overrides[main.get_store] = lambda: store
    return TestClient(main.app)


def test_skip_is_recorded_and_opens_the_day(monkeypatch):
    monkeypatch.setattr(main.get_settings(), "api_token", "testtok")
    store = InMemoryStore()
    try:
        c = _client(store)
        r = c.post("/quiz/skip", json={"reason": "overslept"}, headers=HEADERS)
        assert r.status_code == 200
        assert r.json()["unlocked"] is True
        assert r.json()["skips_today"] == 1

        listed = c.get("/quiz/skips", headers=HEADERS).json()["skips"]
        assert len(listed) == 1
        assert listed[0]["reason"] == "overslept"
        assert listed[0]["at"]  # timestamped, so a run of skips is visible later

        c.post("/quiz/skip", json={"reason": "again"}, headers=HEADERS)
        assert c.post("/quiz/skip", json={}, headers=HEADERS).json()["skips_today"] == 3
    finally:
        main.app.dependency_overrides.clear()


def test_skip_needs_the_token():
    store = InMemoryStore()
    try:
        r = _client(store).post("/quiz/skip", json={"reason": "x"})
        assert r.status_code == 401
    finally:
        main.app.dependency_overrides.clear()
