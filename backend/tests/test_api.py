import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.models import Article, Issue, Question, Reading, Task
from app.store import InMemoryStore

HEADERS = {"Authorization": "Bearer change-me"}


def make_issue(day: str) -> Issue:
    qs = [
        Question(id=f"q{i}", prompt=f"Question {i}?", choices=["a", "b", "c", "d"], answer_index=0)
        for i in range(10)
    ]
    arts = [
        Article(kind=k, title=k, body="word " * 700)
        for k in ("missed_news", "research", "wildcard")
    ]
    return Issue(
        date=day,
        readings=[Reading(label="Gospel", reference="Lk 1:1", text="text")],
        articles=arts,
        questions=qs,
    )


@pytest.fixture
def client():
    store = InMemoryStore()
    day = main.today()
    store.issues[day] = make_issue(day)
    main.app.dependency_overrides[main.get_store] = lambda: store
    c = TestClient(main.app)  # lifespan (Atlas, scheduler) not started
    c.store = store
    c.day = day
    yield c
    main.app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"ok": True}


def test_endpoints_need_token(client):
    assert client.get("/issue/today").status_code == 401
    assert client.get("/quiz/today").status_code == 401


def test_quiz_hides_answers(client):
    r = client.get("/quiz/today", headers=HEADERS).json()
    assert len(r) == 10
    assert "answer_index" not in r[0]


def test_gate_unlocks_on_good_score(client):
    answers = {f"q{i}": 0 for i in range(8)} | {"q8": 1, "q9": 1}  # 80 percent
    r = client.post("/quiz/submit", json={"answers": answers}, headers=HEADERS).json()
    assert r["result"] == "unlocked" and r["tries_used"] == 1


def test_gate_two_tries_then_locked(client):
    bad = {f"q{i}": 1 for i in range(10)}
    first = client.post("/quiz/submit", json={"answers": bad}, headers=HEADERS).json()
    second = client.post("/quiz/submit", json={"answers": bad}, headers=HEADERS).json()
    third = client.post("/quiz/submit", json={"answers": bad}, headers=HEADERS).json()
    assert [first["result"], second["result"], third["result"]] == ["retry", "locked", "locked"]


def test_task_update_and_briefing(client):
    client.store.tasks["t1"] = Task(id="t1", date=client.day, title="Send report")
    client.store.tasks["t2"] = Task(id="t2", date=client.day, title="Gym", status="done")
    r = client.post(
        "/tasks/t1", json={"status": "pushed", "push_to": "2026-12-01"}, headers=HEADERS
    ).json()
    assert r["status"] == "pushed" and r["push_to"] == "2026-12-01"
    text = client.get("/jarvis/briefing", headers=HEADERS).json()["text"]
    assert "Send report" in text and "1 done" in text


def test_unknown_task_404(client):
    r = client.post("/tasks/nope", json={"status": "done"}, headers=HEADERS)
    assert r.status_code == 404
