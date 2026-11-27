# Deploying the backend

The backend must run all day: the 6:00 issue build and 10:30pm check are scheduled inside it.
Run exactly one instance (two would fire every job twice).

## Railway (you already use it for Deem)

1. New project, deploy from `Deli-oi/smart-alarm`, root directory `backend`.
2. Variables: `MONGODB_URI`, `MONGODB_DB=smart_alarm`, `ANTHROPIC_API_KEY`, `FISH_API_KEY`,
   `API_TOKEN` (long random string), `GITHUB_USER=Deli-oi`, `GITHUB_TOKEN` (read-only fine-grained PAT).
3. Generate a public domain, then open `https://<domain>/health`.
4. In the iPhone app, enter that URL and the same `API_TOKEN` under Server.
5. In Atlas, replace the open `0.0.0.0/0` access entry with the host's outbound IPs if it has static ones.

Any host that runs a Docker container works the same way (Fly.io, a small VPS).

## Notes

- The app refuses to start with the default token unless `DEBUG=true`.
- `GET /issue/today` returns 404 until the 6:00 job has run; the app then shows its cached copy.
- The 10:30pm result is read from `GET /evening/summary` until push notifications exist.

## Connecting your calendar and inbox
- `ICS_URL`: Google Calendar, Settings, your calendar, "Secret address in iCal format". Treat it like a password.
- `GMAIL_USER` and `GMAIL_APP_PASSWORD`: turn on 2-step verification, then create an app password. Read-only.
- `FISH_VOICE_ID`: optional, defaults to the voice in `docs/VOICE.md`.
- Open the web preview, Settings, and enter the server URL and `API_TOKEN` to see it live.
