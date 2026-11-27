"""Scheduled jobs. Persisted in Atlas through APScheduler's MongoDB job store,
so they survive a restart of the backend host."""

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient

from .config import get_settings
from .db import get_db
from .jobs import run_daily_issue
from .llm import claude_complete
from .store import MongoStore


async def build_daily_issue() -> None:
    """6:00 job: readings, three articles, critical-issue check, recall questions."""
    from .main import today  # local import avoids a cycle

    await run_daily_issue(today(), MongoStore(get_db()), claude_complete)


async def build_evening_check() -> None:
    """10:30pm job: gather leftover tasks and push a notification."""
    # Phase 4 (needs sources connected and a paid Apple developer account for push)


def make_scheduler() -> AsyncIOScheduler:
    s = get_settings()
    store = MongoDBJobStore(
        database=s.mongodb_db, collection="apscheduler_jobs", client=MongoClient(s.mongodb_uri)
    )
    scheduler = AsyncIOScheduler(jobstores={"default": store}, timezone=s.timezone)
    scheduler.add_job(
        build_daily_issue, "cron", hour=6, minute=0, id="daily_issue", replace_existing=True
    )
    scheduler.add_job(
        build_evening_check, "cron", hour=22, minute=30, id="evening_check", replace_existing=True
    )
    return scheduler
