"""Source adapters feed the 10:30pm check. Each returns normalized records."""

from typing import Protocol

from pydantic import BaseModel


class SourceRecord(BaseModel):
    source: str  # gmail, github, drive, calendar, ...
    external_id: str  # stable id inside that source (message id, commit sha, ...)
    when: str  # ISO timestamp
    text: str  # subject, commit message, file title; used for matching
    url: str = ""


class SourceAdapter(Protocol):
    name: str

    async def fetch_since(self, since_iso: str) -> list[SourceRecord]:
        """Everything new in this source since the given ISO time."""
        ...
