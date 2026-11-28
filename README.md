# Smart Alarm

A personalized wake-up system: a 7:00 alarm, a 15-minute newsletter, a recall gate, an opt-in "Jarvis" voice rundown, and a 10:30pm leftover check.

- `ios/` - SwiftUI app (iOS 26+, AlarmKit). Built in Xcode.
- `backend/` - Python (FastAPI) with MongoDB Atlas. Reads and grades; it never calls Claude.
- `preview/` + `site/` - the web app. `preview/build.py` writes `site/index.html`.
- `automation/` - the prompts the scheduled tasks on the Claude account run.
- `docs/` - **start with `DECISIONS.md`**, then `AUTOMATION.md` and `DEPLOY.md`.

## Backend quick start

```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in values
pytest
uvicorn app.main:app --reload
```

## Build order

Phase 0 alarm/push/Apple Notes spike, 1 reader, 2 backend and issue builder, 3 recall gate and Notes page, 4 sources and 10:30pm check, 5 calendar loop, 6 Jarvis (opt-in), 7 polish and TV.
