"""Demo content for local development. Never used in production paths."""

from .models import Article, Issue, Question, Reading, Task

_QA = [
    ("What do central banks watch because wages feed into prices?", ["The job market", "Rainfall", "Stock splits", "Shipping rates"], 0),
    ("Strong hiring tends to push inflation which way?", ["Down", "Up", "No effect", "Only on weekends"], 1),
    ("In the 2006 study, what did one group do after reading?", ["Took a recall test", "Slept", "Highlighted", "Left"], 0),
    ("A week later, who remembered more?", ["The rereaders", "The tested group", "Both the same", "Neither"], 1),
    ("Why does retrieval practice work?", ["It is quicker", "Pulling a fact from memory strengthens it", "It is fun", "It avoids notes"], 1),
    ("Where was the Antikythera mechanism found?", ["A Greek shipwreck", "An Egyptian tomb", "A Roman villa", "A Turkish library"], 0),
    ("What did it predict?", ["Harvests", "Eclipses", "Wars", "Tides only"], 1),
    ("When was it found?", ["1801", "1901", "1951", "2001"], 1),
]


def demo_issue(day: str) -> Issue:
    return Issue(
        date=day,
        readings=[Reading(label="Demo", reference="Placeholder", text="The real readings are fetched at 6:00.")],
        reflection="Demo issue for local development.",
        articles=[
            Article(kind="missed_news", title="Why central banks watch the job market", body="Wages feed into prices. " * 40),
            Article(kind="research", title="Retrieval practice beats rereading", body="Testing strengthens memory. " * 40),
            Article(kind="wildcard", title="The Antikythera mechanism", body="An ancient geared device. " * 40),
        ],
        questions=[
            Question(id=f"q{i}", prompt=p, choices=c, answer_index=a) for i, (p, c, a) in enumerate(_QA)
        ],
    )


def demo_tasks(day: str) -> list[Task]:
    return [
        Task(id=f"{day}:t1", date=day, title="Ship the preview", status="done", source="github", note="Detected: commit in your repository"),
        Task(id=f"{day}:t2", date=day, title="Reply to the recruiter"),
    ]


def demo_day(day: str) -> dict:
    """Same shape the morning automation writes into `day_plans`."""
    return {
        "date": day,
        "events": [
            {"start": "10:00", "end": "11:50", "title": "Lecture", "location": "", "all_day": False},
            {"start": "11:30", "end": "12:15", "title": "Advisor meeting", "location": "Lally", "all_day": False},
            {"start": "17:00", "end": "18:00", "title": "Gym", "location": "", "all_day": False},
        ],
        "mail": [
            {"sender": "A recruiter", "subject": "Interview scheduling"},
            {"sender": "A club", "subject": "Annual meeting Tuesday"},
        ],
        "notes": "Demo day plan for local development.",
    }
