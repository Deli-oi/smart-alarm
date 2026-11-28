"""Two schedulers write the evening result. Only one may own it on any given night.

The Claude-account automation runs at 22:27 with the Gmail, Drive, Calendar and chat
connectors. The backend's own job runs at 22:30. With no source credentials the backend
job has no evidence at all, so without this guard it marked nothing done and then
overwrote the automation's summary with an emptier one.
"""

import app.schedule as schedule


async def _fail(*a, **k):  # pragma: no cover - called only if the guard is broken
    raise AssertionError("the evening check ran with no sources configured")


def test_evening_check_is_silent_without_sources(monkeypatch):
    s = schedule.get_settings()
    for name in ("github_user", "github_token", "gmail_user", "gmail_app_password",
                 "nango_url", "nango_secret_key", "nango_drive_connection"):
        monkeypatch.setattr(s, name, "")
    monkeypatch.setattr(schedule, "run_evening_check", _fail)
    import asyncio

    asyncio.run(schedule.build_evening_check())


def test_evening_check_runs_once_github_is_configured(monkeypatch):
    s = schedule.get_settings()
    for name in ("gmail_user", "gmail_app_password", "nango_url", "nango_secret_key",
                 "nango_drive_connection"):
        monkeypatch.setattr(s, name, "")
    monkeypatch.setattr(s, "github_user", "Deli-oi")
    monkeypatch.setattr(s, "github_token", "ghp_example")
    called: list[int] = []

    async def _ran(day, since, store, adapters):
        called.append(len(adapters))

    monkeypatch.setattr(schedule, "run_evening_check", _ran)
    monkeypatch.setattr(schedule, "get_db", lambda: None)
    monkeypatch.setattr(schedule, "MongoStore", lambda db: None)
    import asyncio

    asyncio.run(schedule.build_evening_check())
    assert called == [1]
