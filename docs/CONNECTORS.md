# How connector apps keep your data private, and what we do

Researched 2026-11-27.

## What n8n does
- Credentials (API keys, OAuth tokens) are encrypted before they are saved to the database, using an
  instance key (`N8N_ENCRYPTION_KEY`). If you do not set one, n8n makes a random key on first start and
  keeps it in `~/.n8n`; in Docker without a volume that key is lost on redeploy and every credential must be re-made.
- A database dump alone is useless without the key; the key plus the dump exposes everything. Newer
  versions add a second layer (a data key, encrypted by the instance key) so keys can be rotated.
- Anyone who can edit a workflow can use every credential it references.
- Optionally, secrets can live in an outside vault (HashiCorp Vault, Infisical) and be fetched at run time.

## What Nango, Composio and Pipedream do
- They run the OAuth dance for you (redirect, token exchange, storage, refresh) for hundreds of APIs.
- Nango is open source (Elastic License 2.0) and can be self-hosted, with your own encryption key.
  Composio's credential store is closed source and hosted; they reported a security incident in May 2026
  that made customers rotate keys. Treat any hosted vault as one more place your tokens live.
- These are built for products with many customers. For one person they add a service to run.

## What the MCP standard does
- Remote MCP servers use OAuth 2.1 with PKCE. Tokens are bound to one server (so a token for one server
  cannot be replayed at another), access tokens are short-lived, and refresh tokens are treated like crown jewels.
- This is how the Claude connectors you already have work. Your tokens live with Claude, not in our backend.

## Google specifics that affect us
- An OAuth app left in "Testing" issues refresh tokens that expire after 7 days.
- Publishing it ("In production") without verification is allowed for personal use (under 100 users), with a
  warning screen. Reports differ on whether refresh tokens then stop expiring for sensitive scopes like Gmail
  and Drive, so budget for re-consent until confirmed on your own account.

## What we do
1. **Now, no OAuth:** Calendar through the private iCal link, Gmail through IMAP with an app password.
   Both are read-only, never expire on a 7-day clock, and revoking is one click (reset the iCal link, delete
   the app password). They live in the host's environment variables, not in Atlas.
2. **When OAuth is needed (Drive, Outlook):** store tokens in Atlas only after `app/vault.py` encrypts them
   with `TOKEN_ENC_KEY`, which lives in the host environment only. Read-only scopes, one connection per source.
3. **Hygiene:** never log tokens or message bodies; keep only what matching needs (subject, id, time);
   keep the key backed up separately from the database; rotate by reconnecting.
4. **Later option:** self-hosted Nango if we end up with many OAuth sources. Not worth it for two or three.

## Still to build
- A `connections` collection and the Drive/Outlook OAuth flows using the vault.
- Expiry on stored source records (for example 14 days) so evidence does not pile up.
- A per-source off switch and an audit line each time a source is read.
