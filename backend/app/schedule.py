"""Scheduled jobs. Persisted in Atlas through APScheduler's MongoDB job store,
so they survive a restart of the backend host."""

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient

from .config import get_settings
from .db import get_db
from .jobs import run_daily_issue, run_evening_check
from .llm import claude_complete
from .store import MongoStore


async def build_daily_issue() -> None:
    """6:00 job: readings, three articles, critical-issue check, recall questions."""
    from .main import today  # local import avoids a cycle

    if not get_settings().anthropic_api_key:
        return  # no API key: the Claude-account automation writes the issue instead (docs/AUTOMATION.md)

    from datetime import date

    from .sources.usccb import fetch_readings_text

    async def feed(day: str) -> str:
        return await fetch_readings_text(date.fromisoformat(day))

    await run_daily_issue(today(), MongoStore(get_db()), claude_complete, fetch_readings=feed)


async def build_evening_check() -> None:
    """10:30pm job: gather evidence from sources and save the leftover summary.

    Push delivery comes later (needs a paid Apple developer account); until then the app
    shows the summary from /evening/summary.
    """
    from datetime import datetime, timedelta, timezone

    from .main import today
    from .sources.github import GitHubAdapter

    s = get_settings()
    adapters: list = []
    if s.github_user and s.github_token:
        adapters.append(GitHubAdapter(s.github_user, s.github_token))
    if s.gmail_user and s.gmail_app_password:
        from .sources.gmail_imap import GmailSentAdapter

        adapters.append(GmailSentAdapter(s.gmail_user, s.gmail_app_password))
    if s.nango_url and s.nango_secret_key and s.nango_drive_connection:
        from .oauth.nango import NangoTokens
        from .sources.drive import DriveAdapter

        tokens = NangoTokens(s.nango_url, s.nango_secret_key)

        async def drive_token() -> str:
            return await tokens.access_token(s.nango_drive_integration, s.nango_drive_connection)

        adapters.append(DriveAdapter(drive_token))
    if not adapters:
        # With no source configured this job has no evidence, so it would mark nothing done and
        # then overwrite the summary the Claude-account automation wrote three minutes earlier.
        # Silence is the correct behaviour: see docs/AUTOMATION.md on who owns the evening check.
        return
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    await run_evening_check(today(), since, MongoStore(get_db()), adapters)


async def cache_readings() -> None:
    """Put today's readings in the database before the morning automation looks for them.

    This is the backend's own job: plain httpx from the Railway container, no Claude session
    and nothing to approve. That is the entire point of it, so the 5:37 automation never has
    to ask permission to visit a website at an hour when nobody is awake to grant it.
    """
    from datetime import date as _date

    from .main import today  # local import avoids a cycle
    from .sources.usccb import fetch_sections

    day = today()
    store = MongoStore(get_db())
    if await store.get_readings(day) is not None:
        return
    try:
        await store.save_readings(day, await fetch_sections(_date.fromisoformat(day)))
    except Exception:
        return  # the automation falls back to the citation it can verify


def make_scheduler() -> AsyncIOScheduler:
    s = get_settings()
    store = MongoDBJobStore(
        database=s.mongodb_db, collection="apscheduler_jobs", client=MongoClient(s.mongodb_uri)
    )
    scheduler = AsyncIOScheduler(jobstores={"default": store}, timezone=s.timezone)
    scheduler.add_job(
        build_daily_issue, "cron", hour=6, minute=0, id="daily_issue", replace_existing=True
    )
    # 05:05, half an hour before the automation looks for them, and again at 05:25 in case the
    # feed was briefly down. This is the backend's own job: plain httpx from the Railway
    # container, no Claude session and nothing to approve. That is the entire point of it.
    scheduler.add_job(
        cache_readings, "cron", hour=5, minute=5, id="cache_readings", replace_existing=True
    )
    scheduler.add_job(
        cache_readings, "cron", hour=5, minute=25, id="cache_readings_retry", replace_existing=True
    )
    # 22:20, deliberately before the Claude-account automation at 22:27: this job contributes
    # the sources that need credentials (GitHub), and the automation, running last, sees those
    # marks and has the final say on the summary text.
    scheduler.add_job(
        build_evening_check, "cron", hour=22, minute=20, id="evening_check", replace_existing=True
    )
    return scheduler
