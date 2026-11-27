"""Storage boundary. Routes talk to a Store; Mongo is one implementation.

Tests use InMemoryStore so nothing needs a live database.
"""

from typing import Protocol

from pymongo.asynchronous.database import AsyncDatabase

from .models import Issue, Task


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
        await self.db.quiz_attempts.insert_one({"date": day, "score": score, "passed": passed})

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


class InMemoryStore:
    def __init__(self):
        self.issues: dict[str, Issue] = {}
        self.attempts: list[dict] = []
        self.cards: dict[str, dict] = {}
        self.tasks: dict[str, Task] = {}
        self.summaries: dict[str, str] = {}

    async def save_issue(self, issue: Issue) -> None:
        self.issues[issue.date] = issue

    async def get_issue(self, day: str) -> Issue | None:
        return self.issues.get(day)

    async def tries_used(self, day: str) -> int:
        return sum(1 for a in self.attempts if a["date"] == day)

    async def record_attempt(self, day: str, score: float, passed: bool) -> None:
        self.attempts.append({"date": day, "score": score, "passed": passed})

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
