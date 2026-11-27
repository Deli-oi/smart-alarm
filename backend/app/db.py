from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from .config import get_settings

COLLECTIONS = (
    "issues",
    "quiz_cards",
    "quiz_attempts",
    "tasks",
    "source_records",
    "devices",
)

_client: AsyncMongoClient | None = None


def get_client() -> AsyncMongoClient:
    global _client
    if _client is None:
        _client = AsyncMongoClient(get_settings().mongodb_uri)
    return _client


def get_db() -> AsyncDatabase:
    return get_client()[get_settings().mongodb_db]


async def ensure_indexes(db: AsyncDatabase) -> None:
    """Idempotent index setup, safe to run on every start."""
    await db.issues.create_index("date", unique=True)
    await db.quiz_cards.create_index("due")
    await db.quiz_attempts.create_index([("date", 1)])
    await db.tasks.create_index([("date", 1), ("status", 1)])
    await db.source_records.create_index([("source", 1), ("external_id", 1)], unique=True)
    await db.devices.create_index("token", unique=True)


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
