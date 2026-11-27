from fastapi.testclient import TestClient

from app.main import app, require_token


def test_health_without_lifespan():
    client = TestClient(app)  # no context manager: lifespan (and Atlas) not started
    assert client.get("/health").json() == {"ok": True}


def test_issue_requires_token():
    client = TestClient(app)
    assert client.get("/issue/today").status_code == 401


def test_token_check_accepts_configured_token(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "abc")
    from app.config import get_settings

    get_settings.cache_clear()
    require_token("Bearer abc")  # does not raise
    get_settings.cache_clear()
