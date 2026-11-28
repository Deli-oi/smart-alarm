# Automation on your Claude account (no API key)

Two scheduled tasks on your Claude account do the thinking, so the backend never calls the Claude API
and you pay no per-token cost (they use your normal Claude usage).

| Task | When (America/New_York) | What it does |
|---|---|---|
| Wake-Up daily issue | 5:37 am | Readings from the USCCB feed, three articles, 8 questions, today's calendar and inbox, carried-over tasks. Writes to Atlas. |
| Wake-Up evening check | 10:27 pm | Checks today's open tasks against sent mail, Drive edits, GitHub commits and Claude chats; marks proven ones done; writes the leftover summary. |

The full prompts are in `automation/`. They write straight into Atlas with the MongoDB connector, using the
exact shapes in `backend/app/models.py`. The backend reads the same collections (`issues`, `day_plans`, `tasks`, `summaries`).

Because of this, the backend does not need `ANTHROPIC_API_KEY`, `ICS_URL` or a Gmail app password. With no
Anthropic key set, the backend's own 6:00 Claude job is skipped.

Check a payload before trusting a new prompt change:
`python backend/scripts/validate_payload.py issue payload.json` (also `task`, `day`).

Not yet confirmed: that scheduled runs can reach every connector (MongoDB, Gmail, Calendar, Drive, GitHub).
The first two runs will show; read their reports. Tonight's evening run (10:27 pm) is the first test: it has two
test tasks for 2026-11-27.
