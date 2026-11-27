"""Builds the daily issue. The model call is injected so tests never hit the network."""

import json
import re
from collections.abc import Awaitable, Callable

from .models import Issue

Completer = Callable[[str], Awaitable[str]]

# Goal areas from the "Potential" list; the model picks what is relevant each day.
GOAL_AREAS = [
    "body (training, nutrition, hormonal and metabolic health)",
    "career (CS, supply chain, business, executive function)",
    "law (tax, patent, financial, contract, insurance)",
    "mind (cognitive function, learning)",
    "money (risk, unforeseen expenses, international business)",
    "faith (Catholic daily Mass readings)",
]

TARGET_WORDS = 2750  # about 15 minutes at 190 words per minute


def build_prompt(day: str, readings_text: str) -> str:
    areas = "\n".join(f"- {a}" for a in GOAL_AREAS)
    return f"""Build today's reading issue for {day}. Reply with ONLY one JSON object, no prose.

Today's Catholic Mass readings (verbatim, include them as given):
{readings_text}

Goal areas:
{areas}

Schema:
{{
  "date": "{day}",
  "readings": [{{"label": str, "reference": str, "text": str}}],
  "reflection": str,   // about 150 words tying the Gospel to the day
  "critical": [str],   // usually empty; only truly critical developments for the goals
  "articles": [        // exactly 3, about 700 words each
    {{"kind": "missed_news", "title": str, "source_url": str, "body": str}},
    {{"kind": "research", "title": str, "source_url": str, "body": str}},
    {{"kind": "wildcard", "title": str, "source_url": str, "body": str}}
  ],
  "questions": [       // 8 multiple-choice recall questions on today's readings and articles
    {{"id": "q1", "prompt": str, "choices": [str, str, str, str], "answer_index": int, "topic": str}}
  ]
}}

Rules: use web search for current facts and give real source URLs; do not invent sources;
the whole issue should read in about {TARGET_WORDS} words; write plainly for a screen."""


def parse_issue(raw: str) -> Issue:
    """Pull the JSON object out of a model reply and validate it."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("no JSON object in model reply")
    return Issue(**json.loads(match.group(0)))


async def build_issue(day: str, readings_text: str, complete: Completer, retries: int = 1) -> Issue:
    prompt = build_prompt(day, readings_text)
    last: Exception | None = None
    for _ in range(retries + 1):
        raw = await complete(prompt)
        try:
            return parse_issue(raw)
        except (ValueError, json.JSONDecodeError) as e:  # pydantic errors are ValueErrors
            last = e
            prompt += f"\n\nYour previous reply was invalid ({e}). Reply with valid JSON only."
    raise RuntimeError(f"could not build issue: {last}")
