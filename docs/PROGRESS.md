# Progress

## Done and tested
- Backend (23 tests): issue builder with retries, 6:00 job, recall gate (70 percent, two tries, FSRS cards),
  tasks, Jarvis briefing text, opt-in Fish Audio speech, 10:30pm check with evidence matching, GitHub adapter.
- Swift core package (tests pass on Mac CI) and the app (compiles on Mac CI).

## Not yet verified
- Anything against live Claude, Fish Audio or Atlas (no keys in the build environment).
- The `web_search_20250305` tool name in `backend/app/llm.py`: check against current Anthropic docs.
- Fetching the Catholic readings: the job asks Claude to retrieve them from USCCB; reliability unknown.
- AlarmKit on a device: ring length, the Read button opening the app, the 7:05 safety alarm.
- Whether the AlarmKit entitlement needs a paid Apple Developer account.

## Next
- Gmail, Drive and Calendar adapters (Google OAuth), then Outlook, Claude chats, Claude Code, Apple Notes bridge.
- Calendar loop with approval before any change.
- Jarvis conversation (speech in, Claude tool-use loop, speech out).
- Push notifications (needs the paid developer account).
- Keychain storage for the token in the app.
