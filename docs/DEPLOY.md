# Deploying the backend

The backend is live on Railway, in its own project called **wake-up** (the Deem project is untouched).

- Service: `backend`, deployed from `Deli-oi/smart-alarm`, branch `main`, root directory `/backend`
- URL: `https://backend-production-266d0153.up.railway.app`
- Health check: `/health`, which Railway also uses to gate each deploy
- Every push to `main` redeploys it

Run exactly one instance. Two would fire the scheduled jobs twice.

## Variables

Set on the service in Railway, under Variables:

| Name | What it is |
|---|---|
| `MONGODB_URI` | The Atlas connection string |
| `MONGODB_DB` | `smart_alarm` |
| `API_TOKEN` | A long random string. The app sends it as a bearer token |
| `TOKEN_ENC_KEY` | Fernet key for the OAuth token vault |
| `FISH_API_KEY` | Fish Audio, for the Jarvis voice |
| `FISH_VOICE_ID` | Defaults to the voice in `docs/VOICE.md` |
| `TIMEZONE` | `America/New_York` |
| `STORE` | `mongo` |

No `ANTHROPIC_API_KEY`, no `ICS_URL` and no Gmail app password. The scheduled tasks on the Claude
account read the calendar and inbox through their own connectors and write the day's documents
straight into Atlas, so the backend only reads and grades. See `docs/AUTOMATION.md`.

With no Anthropic key set, the backend's own 6:00 issue job is skipped on purpose.

## Connecting the app

Open the preview, tap **Settings**, enter the server address and the `API_TOKEN`, then
**Save and connect**. The checks list says which part worked and which did not:

- *Cannot reach the server* — the address is wrong, or the service is asleep
- *Token refused* — the token does not match `API_TOKEN` in Railway
- *Today's issue not written yet* — normal before the 5:37 am run; the server is fine

## Local development

    cd backend && STORE=memory DEBUG=true API_TOKEN=testtok python -m uvicorn app.main:app --port 8765
    curl -XPOST -H 'Authorization: Bearer testtok' localhost:8765/dev/seed
    cd site && python -m http.server 8000
    python scripts/e2e_ui.py

`STORE=memory` skips Atlas and the scheduler. `/dev/seed` fills the day with a demo issue, a day
plan and two tasks, and clears the recall attempts so the gate can be run again.

## Notes

- The app refuses to start with the default token unless `DEBUG=true`.
- `GET /issue/today` returns 404 until the day's issue exists; the app says so rather than failing.
- Atlas currently allows every IP so Railway can connect. Narrow it if the host gets static IPs.
