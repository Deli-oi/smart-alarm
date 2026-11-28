"""The checks that would have caught a backend that cannot start.

On 28 November three deploys in a row failed with NameError: cache_readings is not defined,
and every one of them passed CI, because nothing in the suite ever built the scheduler. The
app only does that inside the lifespan, which the tests bypass. These are cheap and they close
that hole: if a job's callable does not resolve, this fails here rather than on Railway.
"""

import importlib
import pkgutil

import app
from app.schedule import make_scheduler

EXPECTED_JOBS = {"daily_issue", "evening_check", "cache_readings", "cache_readings_retry"}


def test_the_scheduler_builds_and_every_job_resolves():
    scheduler = make_scheduler()
    jobs = {j.id: j for j in scheduler.get_jobs()}
    assert set(jobs) == EXPECTED_JOBS, set(jobs) ^ EXPECTED_JOBS
    for job_id, job in jobs.items():
        assert callable(job.func), f"{job_id} has no callable attached"


def test_every_module_imports():
    """A typo in a module nothing imports at test time still breaks the deploy."""
    failed = []
    for mod in pkgutil.walk_packages(app.__path__, prefix="app."):
        try:
            importlib.import_module(mod.name)
        except Exception as exc:  # noqa: BLE001 - the point is to report, not to classify
            failed.append(f"{mod.name}: {exc}")
    assert not failed, failed


def test_the_app_exposes_the_routes_the_phone_calls():
    """The app reads these by hand; a rename here is a silent failure in the app."""
    from app.main import app as api

    paths = {r.path for r in api.routes}
    for path in (
        "/health", "/issue/today", "/quiz/today", "/quiz/submit", "/quiz/skip",
        "/day", "/tasks/today", "/notes", "/notes/today", "/notes/process-now",
        "/readings/today", "/issues", "/regularity", "/evening/summary", "/jarvis/speak",
    ):
        assert path in paths, f"{path} is gone; the app still calls it"
