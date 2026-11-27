from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse

from . import recall
from .briefing import build_briefing
from .config import get_settings
from .db import close_client, ensure_indexes, get_db
from .llm import fish_speech
from .models import GateResponse, Issue, PublicQuestion, SubmitAnswers, Task, TaskUpdate
from .schedule import make_scheduler
from .store import MongoStore, Store


def require_token(authorization: str = Header(default="")) -> None:
    if authorization != f"Bearer {get_settings().api_token}":
        raise HTTPException(status_code=401, detail="bad token")


def get_store() -> Store:
    return MongoStore(get_db())


def today() -> str:
    return datetime.now(ZoneInfo(get_settings().timezone)).date().isoformat()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = get_settings()
    if cfg.api_token == "change-me" and not cfg.debug:
        raise RuntimeError("Set API_TOKEN to a real secret (or DEBUG=true for local dev).")
    await ensure_indexes(get_db())
    scheduler = make_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await close_client()


app = FastAPI(title="Smart Alarm", lifespan=lifespan)
auth = [Depends(require_token)]


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.get("/issue/today", dependencies=auth)
async def issue_today(store: Store = Depends(get_store)) -> Issue:
    """Today's newsletter issue; the app falls back to its cached copy on 404."""
    issue = await store.get_issue(today())
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not built yet")
    return issue


@app.get("/quiz/today", dependencies=auth)
async def quiz_today(store: Store = Depends(get_store)) -> list[PublicQuestion]:
    issue = await store.get_issue(today())
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not built yet")
    return [PublicQuestion(id=q.id, prompt=q.prompt, choices=q.choices) for q in issue.questions]


@app.post("/quiz/submit", dependencies=auth)
async def quiz_submit(body: SubmitAnswers, store: Store = Depends(get_store)) -> GateResponse:
    day = today()
    issue = await store.get_issue(day)
    if issue is None:
        raise HTTPException(status_code=404, detail="issue not built yet")
    tries = await store.tries_used(day)
    if tries >= recall.MAX_TRIES:
        return GateResponse(result="locked", score=0.0, tries_used=tries)

    outcomes = [body.answers.get(q.id) == q.answer_index for q in issue.questions]
    for q, ok in zip(issue.questions, outcomes):
        card_id = f"{day}:{q.id}"
        state = await store.get_card(card_id) or recall.new_card_state()
        new_state, due = recall.review(state, ok)
        await store.put_card(card_id, new_state, due.isoformat())

    result = recall.gate_result(outcomes, tries_used=tries + 1)
    value = recall.score(outcomes)
    await store.record_attempt(day, value, passed=result == "unlocked")
    return GateResponse(result=result, score=value, tries_used=tries + 1)


@app.get("/tasks/today", dependencies=auth)
async def tasks_today(store: Store = Depends(get_store)) -> list[Task]:
    return await store.list_tasks(today())


@app.post("/tasks/{task_id}", dependencies=auth)
async def update_task(task_id: str, body: TaskUpdate, store: Store = Depends(get_store)) -> Task:
    task = await store.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="no such task")
    task = task.model_copy(update=body.model_dump())
    await store.put_task(task)
    return task


@app.get("/jarvis/briefing", dependencies=auth)
async def jarvis_briefing(store: Store = Depends(get_store)) -> dict:
    """The day rundown as text. Does not touch Fish Audio."""
    day = today()
    text = build_briefing(day, await store.list_tasks(day), await store.get_issue(day))
    return {"text": text}


@app.get("/jarvis/speak", dependencies=auth)
async def jarvis_speak(store: Store = Depends(get_store)) -> StreamingResponse:
    """Opt-in voice: only runs when the user taps Jarvis, so credits are spent only then."""
    day = today()
    text = build_briefing(day, await store.list_tasks(day), await store.get_issue(day))
    return StreamingResponse(fish_speech(text), media_type="audio/mpeg")


@app.get("/evening/summary", dependencies=auth)
async def evening_summary(store: Store = Depends(get_store)) -> dict:
    """What the 10:30pm check found, until push notifications are set up."""
    return {"text": await store.get_summary(today())}
