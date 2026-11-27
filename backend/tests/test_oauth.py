import httpx
import pytest

from app.oauth.nango import NangoError, NangoTokens
from app.sources.drive import DriveAdapter


def client(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_nango_returns_access_token_with_bearer_secret():
    seen = {}

    def h(req):
        seen["auth"], seen["path"], seen["q"] = req.headers["authorization"], req.url.path, dict(req.url.params)
        return httpx.Response(200, json={"credentials": {"access_token": "tok-1"}})

    t = NangoTokens("https://n.example/", "sk", client(h))
    assert await t.access_token("google-drive", "me") == "tok-1"
    assert seen == {"auth": "Bearer sk", "path": "/connection/me", "q": {"provider_config_key": "google-drive"}}


async def test_nango_missing_connection_has_clear_error():
    t = NangoTokens("https://n.example", "sk", client(lambda r: httpx.Response(404)))
    with pytest.raises(NangoError, match="connect it first"):
        await t.access_token("google-drive", "me")


async def test_drive_adapter_maps_files_and_sends_token():
    seen = {}

    def h(req):
        seen["auth"], seen["q"] = req.headers["authorization"], req.url.params["q"]
        return httpx.Response(200, json={"files": [{"id": "f1", "name": "Notes.md", "modifiedTime": "2026-11-27T01:00:00Z", "webViewLink": "u"}]})

    async def tok():
        return "tok-2"

    recs = await DriveAdapter(tok, client(h)).fetch_since("2026-11-26T12:00:00Z")
    assert [(r.source, r.text, r.external_id) for r in recs] == [("drive", "Notes.md", "f1")]
    assert seen["auth"] == "Bearer tok-2" and "2026-11-26T12:00:00Z" in seen["q"]
