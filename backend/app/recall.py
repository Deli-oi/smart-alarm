"""Recall gate logic: FSRS scheduling plus the 70 percent / two-try unlock rule."""

from datetime import datetime, timezone

from fsrs import Card, Rating, Scheduler

PASS_THRESHOLD = 0.70
MAX_TRIES = 2

_scheduler = Scheduler()


def new_card_state() -> dict:
    """A fresh FSRS card, as a dict that can be stored in MongoDB."""
    return Card().to_dict()


def review(card_state: dict, correct: bool, now: datetime | None = None) -> tuple[dict, datetime]:
    """Apply one answer to a stored card. Returns (new state, next due time)."""
    now = now or datetime.now(timezone.utc)
    card = Card.from_dict(card_state)
    rating = Rating.Good if correct else Rating.Again
    card, _log = _scheduler.review_card(card, rating, review_datetime=now)
    return card.to_dict(), card.due


def score(answers: list[bool]) -> float:
    if not answers:
        return 0.0
    return sum(answers) / len(answers)


def gate_result(answers: list[bool], tries_used: int) -> str:
    """'unlocked', 'retry', or 'locked' (out of tries; emergency skip is logged elsewhere)."""
    if score(answers) >= PASS_THRESHOLD:
        return "unlocked"
    return "retry" if tries_used < MAX_TRIES else "locked"
