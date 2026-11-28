"""Check an automation payload against the real models before it goes into Atlas.

usage: python scripts/validate_payload.py issue payload.json   (or: task, day)
"""
import json
import sys

from app.models import Issue, Task

kind, path = sys.argv[1], sys.argv[2]
data = json.load(open(path))
if kind == "issue":
    i = Issue(**data)
    print(f"ok issue {i.date}: {len(i.articles)} articles, {len(i.questions)} questions, {i.word_count()} words")
elif kind == "task":
    for t in data:
        Task(**t)
    print(f"ok {len(data)} tasks")
elif kind == "day":
    assert isinstance(data.get("events"), list) and isinstance(data.get("mail"), list) and "date" in data
    print("ok day plan")
