# Working on this repository

Read `docs/DECISIONS.md` before changing the daily flow: several choices look like oversights
until you know why they were made.

The rules below are not general advice. Every one of them is here because it was broken on
28 November 2026 and cost real time. They are mostly about one failure: **reporting that
something worked when it was never checked.**

## Never report a result you have not observed

The worst failure in this project so far was not a bug. It was three deploys in a row that
failed on startup while the summary said "CI green, Railway redeployed". The app silently served
sample content for an hour and the user found it, not the agent.

Before you write that something works, name the evidence to yourself. If there is none, say that
instead. "I changed X; I have not verified it" is a good sentence and costs nothing. "Should
work" and "that's now fixed" are claims, and claims need checking.

### An edit that matches nothing still reports success

A patch that does a string replacement will happily replace zero occurrences and exit 0. That is
exactly how `cache_readings` came to be referenced in `app/schedule.py` and never defined.

After any scripted edit, grep for the thing you just added. For a Python change, import it:

    python -c "from app.schedule import make_scheduler; make_scheduler()"

Prefer the `Edit` tool, which fails loudly when the old text is not found, over `sed` and
`str.replace` in a heredoc, which do not.

### Green CI is not a deployed app

GitHub Actions and Railway are different systems and they disagreed for three commits. After any
push touching `backend/`, check the Railway deployment, not just `gh run list`:

    mcp__Railway__get-status, project b0ae7a28-d127-46b8-8e72-a5db30c3d057

The sandbox cannot reach the Railway host. `WebFetch` on `/health` can, and the Railway HTTP
logs show the status code of any request the user's phone made, which is usually the fastest way
to tell a server fault from an app fault.

### Tests can pass against a backend that cannot start

The suite drives routes through dependency overrides and never runs the app lifespan, so for a
long time nothing built the scheduler. `tests/test_startup.py` now does, and CI runs
`ruff check --select F,E9` first. Keep both. If you add a job, a module or a route the app calls,
it belongs in that test.

## Never present placeholder content as real

The app used to fall back to its built-in sample issue whenever a fetch failed, which looks
exactly like a working app showing the wrong day. It now refuses: a banner names what failed on
every screen, and the affected screens show nothing rather than samples. Samples appear only when
no server is configured.

A Home Screen install on iOS has its own storage, separate from Safari. Connecting in one does
not connect the other, and the symptom is an app showing samples with nothing obviously wrong.
When a report says "still a placeholder", check the Railway HTTP logs first: no requests at all
means nothing is configured in whatever window they are using, which is different from requests
that fail.

Hold yourself to the same standard. If you seed, stub or hand-write data to make something
demonstrable, label it in the data itself and say so in the same breath. Do not let a reader
discover later that what they were looking at was yours.

## Scheduled runs: silence is the failure mode

A scheduled task has nobody to answer a prompt, so any call needing approval hangs until timeout
and the run then reports **success** having written nothing. That cost a morning.

- Never use a destructive database call in an automation. `update-many` with `upsert: true` and
  `$set` of the whole document replaces a document and needs no approval.
- Never fetch a web page in an automation where the backend can fetch it and store the result.
  Each run is a fresh session, so a permission the user granted once does not carry over.
- A run reporting success proves nothing. Check the database for the documents it should have
  written, and compare them against what was there before.

## A check that passes for the wrong reason is worse than no check

The morning task skipped rebuilding an issue because it counted 2,400 words and concluded the
issue was real. The words were all on subjects the user had just said he did not care about. The
guard now tests the article kinds as well as the length.

When you write a guard, ask what a wrong thing that passes it would look like.

## House style

- Plain language in user-facing strings, comments and commit messages. No middle-dot meta strings
  (`A · B · C`), no tracked-out all-caps labels, no hype.
- Comments say *why*, not *what*. The ones worth keeping record a decision or a trap.
- Every interactive element: a visible focus state, a 44px minimum target, an accessible name.
- Run the full end-to-end suite before pushing UI changes; it catches real regressions:

      cd backend && STORE=memory DEBUG=true API_TOKEN=testtok python -m uvicorn app.main:app --port 8765
      curl -XPOST -H 'Authorization: Bearer testtok' localhost:8765/dev/seed
      cd site && python -m http.server 8000
      python scripts/e2e_ui.py

- `preview/template.html` is the source; `site/index.html` is generated by `preview/build.py`.
  Never edit `site/` by hand.
