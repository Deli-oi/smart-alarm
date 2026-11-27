from datetime import datetime, timedelta, timezone

from app import recall


def test_gate_unlocks_at_seventy_percent():
    answers = [True] * 7 + [False] * 3
    assert recall.gate_result(answers, tries_used=1) == "unlocked"


def test_gate_retry_then_locked():
    answers = [True] * 6 + [False] * 4
    assert recall.gate_result(answers, tries_used=1) == "retry"
    assert recall.gate_result(answers, tries_used=2) == "locked"


def test_empty_answers_score_zero():
    assert recall.score([]) == 0.0


def test_correct_answer_pushes_due_date_out_more_than_wrong():
    now = datetime(2026, 11, 27, 7, 0, tzinfo=timezone.utc)
    state = recall.new_card_state()
    _, due_right = recall.review(state, correct=True, now=now)
    _, due_wrong = recall.review(state, correct=False, now=now)
    assert due_right >= due_wrong
    assert due_wrong - now < timedelta(days=1)
