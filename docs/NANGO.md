# Nango (self-hosted OAuth) setup

What it gives us: Nango runs the Google and Microsoft login, stores and refreshes the tokens, and our
backend asks it for a fresh access token each time (`backend/app/oauth/nango.py`). The backend never holds
those tokens itself.

Status: the backend side is built and tested against mock responses. The Nango API shape in the code is from
memory and **unverified**, because the build sandbox could not open docs.nango.dev. Nothing here has run
against a real Nango.

## You need to do
1. Run Nango. Use the official self-hosting guide and its docker compose file from docs.nango.dev (it needs
   its own Postgres, and a dashboard login). Do not copy a compose file from anywhere else. Keep the
   dashboard private, and set Nango's own encryption key before connecting anything.
2. In Google Cloud Console, create an OAuth client. Add the Drive read-only scope
   (`drive.metadata.readonly`; titles and times are all we use). Put your Google account under test users.
   Expect re-login every 7 days while the app is in Testing mode (see `docs/CONNECTORS.md`).
3. In Nango, add a Google Drive integration with that client id and secret, then connect your account
   through Nango's connect screen. Note the integration id and the connection id.
4. Set `NANGO_URL`, `NANGO_SECRET_KEY`, `NANGO_DRIVE_INTEGRATION`, `NANGO_DRIVE_CONNECTION` on the backend.
   The 10:30pm check then counts files you edited that day as evidence.

## Cost and fit
Nango self-hosted adds services to run (about a Postgres plus Nango itself). For two or three sources this
is more machinery than the alternative in `docs/CONNECTORS.md` (our own vault), so decide after the Drive
connection works. Outlook and Gmail via Nango would reuse the same `NangoTokens` class.
