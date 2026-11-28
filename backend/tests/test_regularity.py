"""Start-time consistency. Plain counts only: one data point a day cannot support a score."""

from app.regularity import summarise, window


def _a(date_str: str, hhmm: str, passed: bool = True) -> dict:
    h, m = hhmm.split(":")
    # stored in UTC, read back in New York: 12:00 UTC is 07:00 local in November
    return {"date": date_str, "passed": passed, "score": 1.0,
            "at": f"{date_str}T{int(h) + 5:02d}:{m}:00+00:00"}


def test_no_mornings_yet():
    out = summarise([], "2026-11-28")
    assert out == {"window_days": 14, "mornings": 0, "run": 0, "usual": "", "on_time": 0, "spread_minutes": 0}


def test_a_steady_week():
    days = ["2026-11-%02d" % d for d in range(22, 29)]
    out = summarise([_a(d, "07:0%d" % (i % 5)) for i, d in enumerate(days)], "2026-11-28")
    assert out["mornings"] == 7
    assert out["run"] == 7
    assert out["usual"].startswith("07:0")
    assert out["on_time"] == 7
    assert out["spread_minutes"] <= 30


def test_one_late_morning_breaks_on_time_but_not_the_run():
    days = ["2026-11-%02d" % d for d in range(24, 29)]
    rows = [_a(d, "07:00") for d in days[:-1]] + [_a(days[-1], "09:40")]
    out = summarise(rows, "2026-11-28")
    assert out["run"] == 5
    assert out["on_time"] == 4          # the 9:40 start is not the usual time
    assert out["spread_minutes"] == 160


def test_a_gap_ends_the_run_but_the_days_still_count():
    rows = [_a("2026-11-28", "07:05"), _a("2026-11-26", "07:00"), _a("2026-11-25", "07:10")]
    out = summarise(rows, "2026-11-28")
    assert out["run"] == 1              # yesterday is missing
    assert out["mornings"] == 3


def test_the_first_attempt_of_a_day_is_the_start_not_the_retry():
    rows = [_a("2026-11-28", "07:02"), _a("2026-11-28", "07:40")]
    out = summarise(rows, "2026-11-28")
    assert out["usual"] == "07:02"


def test_the_window_ends_today_and_reaches_back_two_weeks():
    w = window("2026-11-28")
    assert w[0] == "2026-11-28" and w[-1] == "2026-11-15" and len(w) == 14
