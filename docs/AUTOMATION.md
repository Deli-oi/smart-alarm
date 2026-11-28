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

## Who owns the evening check

Two schedulers can write the evening result, so the order matters:

| When | Who | Sources |
|---|---|---|
| 22:20 | The backend's own job | GitHub, and IMAP or Drive if ever configured |
| 22:27 | The Claude-account scheduled task | Gmail sent, Drive, Calendar, Claude chats |

The backend runs first and only marks tasks done. The automation runs last, sees those marks,
and writes the summary text. The backend job returns immediately when no source is configured,
because a run with no evidence marks nothing and would only overwrite the automation's summary
with an emptier one. That is exactly what happened on the first night, 27 November: the
automation wrote its summary at 22:28 and the backend replaced it at 22:30 with
`2 left: ... 0 detected done.`

### Turning on commit detection

Nothing detects GitHub work yet, because the Claude account has no GitHub connector and the
backend has no token. The backend already has the adapter. To switch it on:

1. GitHub, Settings, Developer settings, Fine-grained tokens, Generate new token.
2. Repository access: only `Deli-oi/smart-alarm` (add others later if you want them counted).
3. Permissions: Contents **read-only**. Nothing else.
4. In Railway, add `GITHUB_USER=Deli-oi` and `GITHUB_TOKEN=<the token>`.

From the next night, commits count as evidence that a task is done.

Apple Notes and Outlook are in the original list of sources and are not covered. Outlook has no
connector on the account; Apple Notes is not reachable from a cloud session at all, and would
need the desktop app connected.

## The day log

The app keeps a running log of anything he says during the day. `POST /notes` stamps each entry
with the server's time, `GET /notes/today.md` assembles the day as one markdown file, and the
evening run reads the `notes` collection and acts on it.

What the evening run may do with a note:

| In the note | What happens |
|---|---|
| A time or a plan | A Google Calendar event, after checking it is not already there |
| A message to someone | A Gmail **draft**, never sent |
| Something to do | A task on tomorrow's list, `source: daylog` |
| A thought | Stays in the record, nothing else |

It may never send mail, reply, delete, decline an invitation or edit a file. Anything a note asks
for beyond that list is reported in the summary and left for him.

### Asking for it before 10:30

"Send it to Claude now" sets `process_requested` on the day's `day_log` document. The evening run
clears the flag whether or not it was set. Nothing polls for it yet, so today that flag only
changes what the 10:30 run knows; an on-demand run needs either a message to Claude or an hourly
scheduled task, which would be 24 sessions a day against the account's usage.
