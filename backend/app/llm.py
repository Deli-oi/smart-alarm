"""Claude and Fish Audio clients. Thin on purpose; everything else is injectable."""

from collections.abc import Iterator

from anthropic import AsyncAnthropic

from .config import get_settings


async def claude_complete(prompt: str, *, web_search: bool = True) -> str:
    s = get_settings()
    client = AsyncAnthropic(api_key=s.anthropic_api_key)
    kwargs: dict = {}
    if web_search:
        # Server-side web search tool; confirm the exact tool version against current docs.
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}]
    msg = await client.messages.create(
        model=s.claude_model,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    return "".join(b.text for b in msg.content if b.type == "text")


# One frame of silent 32 kbps mono mp3, repeated. Local dev only: it makes the voice path
# end-to-end testable without spending Fish credits or holding a key.
_SILENT_FRAME = bytes.fromhex("fffb10c4") + bytes(100)


def fish_speech(text: str) -> Iterator[bytes]:
    """Stream mp3 audio for text. Only called when the user taps Jarvis, or by the
    early prefetch one step before it (see EARLY FISH LOADING in preview/template.html)."""
    s = get_settings()
    if not s.fish_api_key:
        if not s.debug:
            raise RuntimeError("FISH_API_KEY is not set")
        for _ in range(40):
            yield _SILENT_FRAME
        return

    from fishaudio import FishAudio

    client = FishAudio(api_key=s.fish_api_key)
    yield from client.tts.stream(text=text, reference_id=s.fish_voice_id, model="s2.1-pro", latency="balanced")
