"""Access tokens from a self-hosted Nango (open-source OAuth broker).

Nango runs the OAuth login, stores and refreshes the tokens (encrypted with its own key), and
hands us a fresh access token on request. We never store Google or Microsoft tokens ourselves.

UNVERIFIED against live docs (the build sandbox could not reach them): the request shape below is
GET {NANGO_URL}/connection/{connection_id}?provider_config_key={integration}
with `Authorization: Bearer <NANGO_SECRET_KEY>`, returning credentials.access_token for OAuth2.
Check docs.nango.dev when wiring it up; only `NangoTokens.access_token` would need to change.
"""

import httpx


class NangoError(Exception):
    pass


class NangoTokens:
    def __init__(self, base_url: str, secret_key: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.secret_key = secret_key
        self._client = client

    async def access_token(self, integration: str, connection_id: str) -> str:
        url = f"{self.base_url}/connection/{connection_id}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        params = {"provider_config_key": integration}
        own = self._client is None
        client = self._client or httpx.AsyncClient(timeout=20)
        try:
            r = await client.get(url, headers=headers, params=params)
        finally:
            if own:
                await client.aclose()
        if r.status_code == 404:
            raise NangoError(f"no connection {connection_id!r} for {integration!r}: connect it first")
        if r.status_code >= 400:
            raise NangoError(f"nango returned {r.status_code}")
        token = (r.json().get("credentials") or {}).get("access_token")
        if not token:
            raise NangoError("nango response had no access_token")
        return token
