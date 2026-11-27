from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException

from .config import get_settings
from .db import close_client, ensure_indexes, get_db
from .schedule import make_scheduler


def require_token(authorization: str = Header(default="")) -> None:
    if authorization != f"Bearer {get_settings().api_token}":
        raise HTTPException(status_code=401, detail="bad token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes(get_db())
    scheduler = make_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await close_client()


app = FastAPI(title="Smart Alarm", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.get("/issue/today", dependencies=[Depends(require_token)])
async def issue_today() -> dict:
    """Today's newsletter issue; the app falls back to its cached copy on 404."""
    doc = await get_db().issues.find_one({"date": date.today().isoformat()}, {"_id": 0})
    if doc is None:
        raise HTTPException(status_code=404, detail="issue not built yet")
    return doc
