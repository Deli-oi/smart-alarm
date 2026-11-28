"""Storage boundary. Routes talk to a Store; Mongo is one implementation.

Tests use InMemoryStore so nothing needs a live database.
"""

from datetime import datetime, timezone
from typing import Protocol

from pymongo.asynchronous.database import AsyncDatabase

from .models import Issue, Note, Task


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store(Protocol):
    async def save_issue(self, issue: Issue) -> None: ...
    async def get_issue(self, day: str) -> Issue | None: ...
    async def tries_used(self, day: str) -> int: ...
    async def record_attempt(self, day: str, score: float, passed: bool) -> None: ...
    async def get_card(self, card_id: str) -> dict | None: ...
    async def put_card(self, card_id: str, state: dict, due: str) -> None: ...
    async def list_tasks(self, day: str) -> list[Task]: ...
    async def put_task(self, task: Task) -> None: ...
    async def get_task(self, task_id: str) -> Task | None: ...
    async def save_summary(self, day: str, text: str) -> None: ...
    async def get_summary(self, day: str) -> str | None: ...
    async def get_day(self, day: str) -> dict | None: ...
    async def save_day(self, day: str, plan: dict) -> None: ...
    async def record_skip(self, day: str, reason: str) -> None: ...
    async def list_skips(self, day: str) -> list[dict]: ...
    async def gate_open(self, day: str) -> bool: ...
    async def recent_mornings(self, days: list[str]) -> list[dict]: ...
    async def save_readings(self, day: str, sections: list[dict]) -> None: ...
    async def get_readings(self, day: str) -> list[dict] | None: ...
    async def list_issue_dates(self, limit: int = 60) -> list[dict]: ...
    async def add_note(self, day: str, note: Note) -> None: ...
    async def list_notes(self, day: str) -> list[Note]: ...
    async def mark_notes_sent(self, day: str, at: str) -> int: ...
    async def set_processing(self, day: str, requested: bool) -> None: ...
    async def processing_requested(self, day: str) -> bool: ...


class MongoStore:
    def __init__(self, db: AsyncDatabase):
        self.db = db

    async def save_issue(self, issue: Issue) -> None:
        await self.db.issues.replace_one({"date": issue.date}, issue.model_dump(), upsert=True)

    async def get_issue(self, day: str) -> Issue | None:
        doc = await self.db.issues.find_one({"date": day}, {"_id": 0})
        return Issue(**doc) if doc else None

    async def tries_used(self, day: str) -> int:
        return await self.db.quiz_attempts.count_documents({"date": day})

    async def record_attempt(self, day: str, score: float, passed: bool) -> None:
        await self.db.quiz_attempts.insert_one(
            {"date": day, "score": score, "passed": passed, "at": _now()}
        )

    async def save_readings(self, day: str, sections: list[dict]) -> None:
        await self.db.readings.update_one(
            {"date": day}, {"$set": {"date": day, "sections": sections, "fetched_at": _now()}}, upsert=True
        )

    async def get_readings(self, day: str) -> list[dict] | None:
        doc = await self.db.readings.find_one({"date": day}, {"_id": 0})
        return doc["sections"] if doc else None

    async def list_issue_dates(self, limit: int = 60) -> list[dict]:
        cur = self.db.issues.find({}, {"_id": 0, "date": 1, "articles.title": 1}).sort("date", -1).limit(limit)
        return [{"date": d["date"], "titles": [a["title"] for a in d.get("articles", [])]} async for d in cur]

    async def recent_mornings(self, days: list[str]) -> list[dict]:
        cur = self.db.quiz_attempts.find({"date": {"$in": days}}, {"_id": 0}).sort("at", 1)
        return [d async for d in cur]

    async def record_skip(self, day: str, reason: str) -> None:
        await self.db.skips.insert_one({"date": day, "reason": reason, "at": _now()})

    async def list_skips(self, day: str) -> list[dict]:
        return [d async for d in self.db.skips.find({"date": day}, {"_id": 0})]

    async def gate_open(self, day: str) -> bool:
        if await self.db.quiz_attempts.count_documents({"date": day, "passed": True}):
            return True
        return bool(await self.db.skips.count_documents({"date": day}))

    async def add_note(self, day: str, note: Note) -> None:
        await self.db.notes.insert_one({"date": day, **note.model_dump()})

    async def list_notes(self, day: str) -> list[Note]:
        docs = [d async for d in self.db.notes.find({"date": day}, {"_id": 0, "date": 0}).sort("at", 1)]
        return [Note(**d) for d in docs]

    async def mark_notes_sent(self, day: str, at: str) -> int:
        """Only entries not already handed over, so a second tap marks nothing twice."""
        r = await self.db.notes.update_many(
            {"date": day, "$or": [{"sent_at": {"$exists": False}}, {"sent_at": ""}]},
            {"$set": {"sent_at": at}},
        )
        return r.modified_count

    async def set_processing(self, day: str, requested: bool) -> None:
        await self.db.day_log.update_one(
            {"date": day},
            {"$set": {"process_requested": requested, "requested_at": _now() if requested else ""}},
            upsert=True,
        )

    async def processing_requested(self, day: str) -> bool:
        doc = await self.db.day_log.find_one({"date": day}, {"_id": 0})
        return bool(doc and doc.get("process_requested"))

    async def get_card(self, card_id: str) -> dict | None:
        doc = await self.db.quiz_cards.find_one({"_id": card_id})
        return doc["state"] if doc else None

    async def put_card(self, card_id: str, state: dict, due: str) -> None:
        await self.db.quiz_cards.replace_one(
            {"_id": card_id}, {"_id": card_id, "state": state, "due": due}, upsert=True
        )

    async def list_tasks(self, day: str) -> list[Task]:
        return [Task(**d) async for d in self.db.tasks.find({"date": day}, {"_id": 0})]

    async def put_task(self, task: Task) -> None:
        await self.db.tasks.replace_one({"id": task.id}, task.model_dump(), upsert=True)

    async def get_task(self, task_id: str) -> Task | None:
        doc = await self.db.tasks.find_one({"id": task_id}, {"_id": 0})
        return Task(**doc) if doc else None

    async def save_summary(self, day: str, text: str) -> None:
        await self.db.summaries.replace_one({"date": day}, {"date": day, "text": text}, upsert=True)

    async def get_summary(self, day: str) -> str | None:
        doc = await self.db.summaries.find_one({"date": day})
        return doc["text"] if doc else None

    async def get_day(self, day: str) -> dict | None:
        """Calendar and mail for a day, written by the automation (or any other writer)."""
        return await self.db.day_plans.find_one({"date": day}, {"_id": 0})

    async def save_day(self, day: str, plan: dict) -> None:
        await self.db.day_plans.replace_one({"date": day}, {**plan, "date": day}, upsert=True)


class InMemoryStore:
    def __init__(self):
        self.issues: dict[str, Issue] = {}
        self.attempts: list[dict] = []
        self.cards: dict[str, dict] = {}
        self.tasks: dict[str, Task] = {}
        self.summaries: dict[str, str] = {}
        self.days: dict[str, dict] = {}
        self.skips: list[dict] = []
        self.readings: dict[str, list[dict]] = {}
        self.notes: list[tuple[str, Note]] = []
        self.processing: set[str] = set()

    async def save_issue(self, issue: Issue) -> None:
        self.issues[issue.date] = issue

    async def get_issue(self, day: str) -> Issue | None:
        return self.issues.get(day)

    async def tries_used(self, day: str) -> int:
        return sum(1 for a in self.attempts if a["date"] == day)

    async def record_attempt(self, day: str, score: float, passed: bool) -> None:
        self.attempts.append({"date": day, "score": score, "passed": passed, "at": _now()})

    async def save_readings(self, day: str, sections: list[dict]) -> None:
        self.readings[day] = sections

    async def get_readings(self, day: str) -> list[dict] | None:
        return self.readings.get(day)

    async def list_issue_dates(self, limit: int = 60) -> list[dict]:
        rows = [{"date": d, "titles": [a.title for a in i.articles]} for d, i in self.issues.items()]
        return sorted(rows, key=lambda r: r["date"], reverse=True)[:limit]

    async def recent_mornings(self, days: list[str]) -> list[dict]:
        return sorted([a for a in self.attempts if a["date"] in days], key=lambda a: a.get("at", ""))

    async def record_skip(self, day: str, reason: str) -> None:
        self.skips.append({"date": day, "reason": reason, "at": _now()})

    async def list_skips(self, day: str) -> list[dict]:
        return [s for s in self.skips if s["date"] == day]

    async def gate_open(self, day: str) -> bool:
        passed = any(a["date"] == day and a["passed"] for a in self.attempts)
        return passed or any(s["date"] == day for s in self.skips)

    async def add_note(self, day: str, note: Note) -> None:
        self.notes.append((day, note))

    async def list_notes(self, day: str) -> list[Note]:
        return sorted([n for d, n in self.notes if d == day], key=lambda n: n.at)

    async def mark_notes_sent(self, day: str, at: str) -> int:
        n = 0
        for d, note in self.notes:
            if d == day and not note.sent_at:
                note.sent_at = at
                n += 1
        return n

    async def set_processing(self, day: str, requested: bool) -> None:
        self.processing.add(day) if requested else self.processing.discard(day)

    async def processing_requested(self, day: str) -> bool:
        return day in self.processing

    async def get_card(self, card_id: str) -> dict | None:
        c = self.cards.get(card_id)
        return c["state"] if c else None

    async def put_card(self, card_id: str, state: dict, due: str) -> None:
        self.cards[card_id] = {"state": state, "due": due}

    async def list_tasks(self, day: str) -> list[Task]:
        return [t for t in self.tasks.values() if t.date == day]

    async def put_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    async def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    async def save_summary(self, day: str, text: str) -> None:
        self.summaries[day] = text

    async def get_summary(self, day: str) -> str | None:
        return self.summaries.get(day)

    async def get_day(self, day: str) -> dict | None:
        return self.days.get(day)

    async def save_day(self, day: str, plan: dict) -> None:
        self.days[day] = {**plan, "date": day}
