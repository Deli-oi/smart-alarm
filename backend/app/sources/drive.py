"""Google Drive evidence for the 10:30pm check: files you modified since the cutoff.

Read-only scope (drive.metadata.readonly is enough): we use titles and times only, never contents.
"""

import httpx

from .base import SourceRecord

API = "https://www.googleapis.com/drive/v3/files"


class DriveAdapter:
    name = "drive"

    def __init__(self, get_token, client: httpx.AsyncClient | None = None):
        self._get_token = get_token  # async () -> access token
        self._client = client

    async def fetch_since(self, since_iso: str) -> list[SourceRecord]:
        token = await self._get_token()
        params = {
            "q": f"modifiedTime > '{since_iso}' and trashed = false and 'me' in owners",
            "fields": "files(id,name,modifiedTime,webViewLink)",
            "orderBy": "modifiedTime desc",
            "pageSize": "50",
        }
        own = self._client is None
        client = self._client or httpx.AsyncClient(timeout=20)
        try:
            r = await client.get(API, params=params, headers={"Authorization": f"Bearer {token}"})
            r.raise_for_status()
        finally:
            if own:
                await client.aclose()
        return [
            SourceRecord(
                source="drive",
                external_id=f["id"],
                when=f["modifiedTime"],
                text=f["name"],
                url=f.get("webViewLink", ""),
            )
            for f in r.json().get("files", [])
        ]
