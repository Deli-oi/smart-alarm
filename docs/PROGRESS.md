# Progress

## Done and tested
- Backend (26 tests, CI on every push): issue builder with retries, 6:00 job, recall gate (70 percent, two tries,
  FSRS cards), tasks, Jarvis briefing text, opt-in Fish Audio speech (voice set by `FISH_VOICE_ID`),
  10:30pm check with evidence matching, GitHub adapter.
- `/day`: today's calendar (Google private iCal link, no OAuth, overlaps flagged) and inbox subjects
  (Gmail over IMAP with an app password, read-only). Each source reports in `errors` when not set up.
- Local dev mode: `STORE=memory DEBUG=true`, then `POST /dev/seed`. No Atlas needed.
- Web client (`preview/template.html`): the same UI runs on sample data or live against the API
  (Settings: server URL and token). `scripts/e2e_ui.py` drives it in headless Chrome against a local
  backend: seeded issue, failed first attempt, passed second attempt, Today with calendar overlaps, evening tasks.
- Swift core package (tests pass on Mac CI), including the `/day` models, and the app (compiles on Mac CI).

## Not yet verified
- Anything against live Claude, Fish Audio or Atlas (no keys in the build environment).
- The Fish voice by ear. Candidates: Alok (default) and F1; sample links in `docs/VOICE.md`.
- The `web_search_20250305` tool name in `backend/app/llm.py`: check against current Anthropic docs.
- Fetching the Catholic readings: the job asks Claude to retrieve them from USCCB; reliability unknown.
- AlarmKit on a device: ring length, the Read button opening the app, the 7:05 safety alarm.
- Whether the AlarmKit entitlement needs a paid Apple Developer account.
- The IMAP and iCal adapters against real accounts (tested with fixtures only).

## Next
- Drive, Outlook, Claude chats, Claude Code and Apple Notes adapters for the evening check.
- Calendar loop with approval before any change.
- Jarvis conversation (speech in, Claude tool-use loop, speech out).
- Push notifications (needs the paid developer account).
- Keychain storage for the token in the app; the app reading `/day`.
