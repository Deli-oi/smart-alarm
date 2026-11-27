import httpx

from .base import SourceRecord


class GitHubAdapter:
    """Your commits and pushed events since a time, via the GitHub REST API.

    Needs a fine-grained personal access token with read access to your repos.
    """

    name = "github"

    def __init__(self, user: str, token: str, client: httpx.AsyncClient | None = None):
        self.user = user
        self.token = token
        self._client = client

    async def fetch_since(self, since_iso: str) -> list[SourceRecord]:
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        owns = self._client is None
        client = self._client or httpx.AsyncClient(timeout=20)
        try:
            r = await client.get(
                f"https://api.github.com/users/{self.user}/events", headers=headers
            )
            r.raise_for_status()
            return parse_events(r.json(), since_iso)
        finally:
            if owns:
                await client.aclose()


def parse_events(events: list[dict], since_iso: str) -> list[SourceRecord]:
    out: list[SourceRecord] = []
    for e in events:
        if e.get("type") != "PushEvent" or e.get("created_at", "") < since_iso:
            continue
        repo = e["repo"]["name"]
        for c in e["payload"].get("commits", []):
            out.append(
                SourceRecord(
                    source="github",
                    external_id=c["sha"],
                    when=e["created_at"],
                    text=f"{repo}: {c['message'].splitlines()[0]}",
                    url=f"https://github.com/{repo}/commit/{c['sha']}",
                )
            )
    return out
