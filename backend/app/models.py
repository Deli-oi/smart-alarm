from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Reading(BaseModel):
    label: str  # e.g. "First Reading", "Gospel"
    reference: str  # e.g. "Is 2:1-5"
    text: str


class Article(BaseModel):
    kind: Literal["missed_news", "research", "wildcard"]
    title: str
    source_url: str = ""
    body: str  # about 700 words, written for reading on a screen


class Question(BaseModel):
    id: str
    prompt: str
    choices: list[str] = Field(min_length=2, max_length=5)
    answer_index: int
    topic: str = ""  # which reading or article it tests

    @field_validator("answer_index")
    @classmethod
    def _in_range(cls, v: int, info) -> int:
        choices = info.data.get("choices") or []
        if not 0 <= v < len(choices):
            raise ValueError("answer_index out of range")
        return v


class Issue(BaseModel):
    date: str  # YYYY-MM-DD
    readings: list[Reading]
    reflection: str = ""
    critical: list[str] = []  # rare; empty on most days
    articles: list[Article] = Field(min_length=3, max_length=3)
    questions: list[Question] = Field(min_length=6)

    def word_count(self) -> int:
        parts = [self.reflection] + [r.text for r in self.readings] + [a.body for a in self.articles]
        return sum(len(p.split()) for p in parts)


class PublicQuestion(BaseModel):
    """What the phone sees: no answers, so the gate can't be read off the wire."""

    id: str
    prompt: str
    choices: list[str]


class SubmitAnswers(BaseModel):
    answers: dict[str, int]  # question id -> chosen index


class Note(BaseModel):
    """One thing he said during the day. The server stamps the time, not the phone."""

    at: str  # ISO 8601, UTC
    text: str = Field(min_length=1, max_length=4000)
    kind: Literal["note", "reply"] = "note"


class NoteRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    kind: Literal["note", "reply"] = "note"


class SkipRequest(BaseModel):
    """Why the gate was skipped. Free text, kept short, written to the record."""

    reason: str = Field(default="", max_length=200)


class GateResponse(BaseModel):
    result: Literal["unlocked", "retry", "locked"]
    score: float
    tries_used: int


class Task(BaseModel):
    id: str
    date: str
    title: str
    status: Literal["open", "done", "not_done", "pushed"] = "open"
    note: str = ""
    push_to: str = ""  # YYYY-MM-DD when pushed
    source: str = ""  # which source detected it (gmail, github, ...)


class TaskUpdate(BaseModel):
    status: Literal["done", "not_done", "pushed"]
    note: str = ""
    push_to: str = ""
