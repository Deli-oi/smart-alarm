# Progress

## Done and tested
- Backend (36 tests, CI on every push): issue builder with retries, 6:00 job, recall gate (70 percent, two tries,
  FSRS cards), tasks, Jarvis briefing text, opt-in Fish Audio speech (voice set by `FISH_VOICE_ID`),
  10:30pm check with evidence matching, GitHub adapter.
- `/day`: today's calendar (Google private iCal link, no OAuth, overlaps flagged) and inbox subjects
  (Gmail over IMAP with an app password, read-only). Each source reports in `errors` when not set up.
- Local dev mode: `STORE=memory DEBUG=true`, then `POST /dev/seed`. No Atlas needed.
- Web client (`preview/template.html`): the same UI runs on sample data or live against the API
  (Settings: server URL and token). `scripts/e2e_ui.py` drives it in headless Chrome against a local
  backend: seeded issue, failed first attempt, passed second attempt, Today with calendar overlaps, evening tasks.
- Swift core package (tests pass on Mac CI), including the `/day` models, and the app (compiles on Mac CI).

## Research results (2026-11-27)
- Web search tool: `web_search_20250305` is a current, documented tool type (newer versions add dynamic filtering). Keep it.
- AlarmKit entitlement: Apple forum guidance says no special entitlement or portal capability exists; only
  `NSAlarmKitUsageDescription` in Info.plist. A developer also ran an AlarmKit prototype on a free Personal Team.
  So a paid account is probably not needed for the alarm itself. Not confirmed by Apple docs; still test on the phone.
- AlarmKit risks found: overlapping alerting alarms can silence each other (so the safety alarm moved from 7:05 to 7:10),
  late delivery on a locked device, and iOS 27 beta regressions. Alarms break through all Focus modes.
- Readings: USCCB publishes `https://bible.usccb.org/readings.rss` with the full text; implemented in `sources/usccb.py`
  with Claude web search as the fallback. Today's real readings are Revelation 20 and Luke 21, so the earlier placeholder was wrong.
- Connector privacy research: see `docs/CONNECTORS.md`.

## Not yet verified
- Anything against live Claude, Fish Audio or Atlas (no keys in the build environment).
- The Fish voice by ear. Candidates: F1 (default) and Alok; sample links in `docs/VOICE.md`.
- The USCCB feed parser against the live feed from the real host (tested on a reconstructed fixture; the build sandbox cannot reach USCCB).
- AlarmKit on a device: ring length, the Read button opening the app, the 7:10 safety alarm and overlap behavior.
- Whether a free Apple ID can install and run AlarmKit (forum evidence says yes; unconfirmed).
- The IMAP and iCal adapters against real accounts (tested with fixtures only).

## Next
- Outlook adapter on the same Nango client. Drive adapter is built (`docs/NANGO.md`), untested live. (Gmail sent mail already counts as evidence once the IMAP login is set), Claude chats, Claude Code and Apple Notes adapters for the evening check.
- Calendar loop with approval before any change.
- Jarvis conversation (speech in, Claude tool-use loop, speech out).
- Push notifications (needs the paid developer account).
- Keychain storage for the token in the app; the app reading `/day`.
